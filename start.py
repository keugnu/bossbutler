#!/usr/bin/python3

import os
import sys

from dotenv import load_dotenv

import utils
from bot import Bot


log = utils.setup_log()
dotenv_path = utils.find(os.path.dirname(os.path.abspath(__file__)), '.env_debug' if sys.argv[1] == 'debug' else '.env')
load_dotenv(dotenv_path)
token = os.getenv('DISCORD_TOKEN')
bot = Bot(pfx='!')


@bot.event
async def on_disconnect():
    log.warning('Removing last video files before disconnecting.')
    for guild in bot.guilds:
        path = bot.settings.get(guild.id).get('yt_file')
        if os.path.exists(path):
            os.remove(path)
            log.warning(f'Removed {path}')


@bot.event
async def on_ready():
    guilds = await bot.fetch_guilds().flatten()
    log.info(f'I have connected to {", ".join([g.name for g in guilds])}')
    await bot.bootstrap_settings(bot)
    bot.init_spawn_data(bot)
    bot.start_tasks(bot)


try:
    bot.add_cogs(bot)
    log.info('Starting...')
    bot.loop.run_until_complete(bot.start(token))
except (SystemExit, KeyboardInterrupt) as e:
    log.critical(f'Encountered {type(e)}: {e}. Stopping!')
    bot.loop.run_until_complete(bot.logout())
    bot.loop.close()
    sys.exit(1)
