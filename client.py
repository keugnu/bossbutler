import shutil
import os
import logging
from discord.ext import commands

import utils


class Bot(commands.Bot):
    def __init__(self, pfx):
        super().__init__(command_prefix=pfx)

        self.yt_title, self.yt_file = utils.download_yt()
        self.ffmpeg = shutil.which('ffmpeg')
        self.wakeup = 'wakeup-call'
