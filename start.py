#!/usr/bin/python3

import os

from dotenv import load_dotenv

import utils
from bot import Bot


log = utils.setup_log()
dotenv_path = utils.find(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)
token = os.getenv('DISCORD_TOKEN')
bot = Bot(pfx='!')


@bot.event
async def on_disconnect():
    log.warning('Removing last video file before disconnecting.')
    os.remove(bot.yt_file)


@bot.event
async def on_ready():
    guilds = await bot.fetch_guilds().flatten()
    log.info(f'I have connected to {", ".join([g.name for g in guilds])}')


try:
    bot.add_cogs(bot)
    log.info('Starting...')
    bot.loop.run_until_complete(bot.start(token))
except (SystemExit, KeyboardInterrupt) as e:
    log.critical(f'Encountered {type(e)}: {e}. Stopping!')
    bot.loop.run_until_complete(bot.logout())
    bot.loop.close()
