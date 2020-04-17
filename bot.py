import shutil

from discord.ext import commands

import utils
from cog import alerts, settings, control


class Bot(commands.Bot):
    def __init__(self, pfx):
        super().__init__(command_prefix=pfx)

        self.yt_title, self.yt_file = utils.download_yt()
        self.ffmpeg = shutil.which('ffmpeg')
        self.wakeup = None

    @staticmethod
    def add_cogs(bot):
        any(map(bot.add_cog, (alerts.Alerts(bot), settings.Settings(bot), control.Control(bot))))
