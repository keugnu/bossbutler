#!/usr/bin/python3

import os
import sys

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


#@bot.event
#async def on_ready():
#    guilds = await bot.fetch_guilds().flatten()
#    log.info(f'I have connected to {", ".join([g.name for g in guilds])}')


@bot.event
async def on_ready():
    guilds = await bot.fetch_guilds().flatten()
    log.info(f'I have connected to {", ".join([g.name for g in guilds])}')
    try:
        # in case the bot disconnected inadvertently, make sure the file still exists
        with open(bot.yt_file) as f:
            pass
    except (OSError, TypeError):
        if not bot.yt_url:
            log.info('Setting the alarm for the first time.')
        else:
            log.error(f'Could not find {bot.yt_file}. Redownloading it.')

        bot.yt_url, bot.yt_tile, bot.yt_file = utils.download_yt(bot.yt_url)

try:
    bot.add_cogs(bot)
    log.info('Starting...')
    bot.loop.run_until_complete(bot.start(token))
except (SystemExit, KeyboardInterrupt) as e:
    log.critical(f'Encountered {type(e)}: {e}. Stopping!')
    bot.loop.run_until_complete(bot.logout())
    bot.loop.close()
    sys.exit(1)
