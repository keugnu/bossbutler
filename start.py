import os
import logging
import shutil

from dotenv import load_dotenv
from discord.ext import commands

import utils

from cog import alerts, settings, control


log = logging.getLogger('bossbutler')
log.setLevel(logging.DEBUG)
handler = logging.handlers.TimedRotatingFileHandler('/var/log/bossbutler.log', when='d')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(name)s:%(levelname)s:%(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)
dotenv_path = utils.find(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)
token = os.getenv('DISCORD_TOKEN')


class Bot(commands.Bot):
    def __init__(self, pfx):
        super().__init__(command_prefix=pfx)

        self.yt_title, self.yt_file = utils.download_yt()
        self.ffmpeg = shutil.which('ffmpeg')
        self.wakeup = 'wakeup-call'


bot = Bot(pfx='!')
any(map(bot.add_cog, (alerts.Alerts(bot), settings.Settings(bot), control.Control(bot))))


@bot.event
async def on_disconnect():
    log.info('Removing last video file before disconnecting.')
    os.remove(bot.yt_file)


@bot.event
async def on_ready():
    guilds = await bot.fetch_guilds().flatten()
    log.info(f'I have connected to {", ".join([g.name for g in guilds])}')


try:
    bot.loop.run_until_complete(bot.start(token))
except (SystemExit, KeyboardInterrupt):
    log.info('Removing last video file before disconnecting.')
    os.remove(bot.yt_file)
    bot.loop.close()
