import os
import shutil

from discord.ext import commands

import utils
from cog import alerts, settings, control


class Bot(commands.Bot):
    def __init__(self, pfx):
        super().__init__(command_prefix=pfx)

        self.yt_url = None
        self.yt_title = None
        self.yt_file = None
        self.ffmpeg = shutil.which('ffmpeg')
        self.wakeup = None
        self.announcements = None

        assert os.path.exists(self.ffmpeg)

    @staticmethod
    def add_cogs(bot):
        any(map(bot.add_cog, (alerts.Alerts(bot), settings.Settings(bot), control.Control(bot))))
