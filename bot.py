import os
import marshal
import shutil

from discord.ext import commands

import utils
from cog import alerts, settings, control, tasks

class Bot(commands.Bot):
    def __init__(self, pfx):
        super().__init__(command_prefix=pfx)

        self.yt_url = None
        self.yt_title = None
        self.yt_file = None
        self.ffmpeg = shutil.which('ffmpeg')
        self.wakeup = None
        self.announcements = None
        self.spawn_data_file = utils.find(os.path.dirname(__file__), 'spawn_data.bin')
        self.leadership_channel = None

        assert os.path.exists(self.ffmpeg)

    @staticmethod
    def add_cogs(bot):
        any(map(bot.add_cog, (alerts.Alerts(bot), settings.Settings(bot), control.Control(bot))))

    @staticmethod
    def start_tasks(bot):
        bot.add_cog(tasks.Tasks(bot))

    @staticmethod
    def init_spawn_data(bot):
        try:
            with open(bot.spawn_data_file):
                return
        except (FileNotFoundError, TypeError):
            bot.spawn_data_file = os.path.join(os.path.dirname(__file__), 'spawn_data.bin')

            with open(bot.spawn_data_file, 'wb') as f:
                default_data = {
                    'azu': {
                        'up': [],
                        'down': []
                    },
                    'kazz': {
                        'up': [],
                        'down': []
                    },
                    'green': {
                        'up': [],
                        'down': []
                    }
                }
                marshal.dump(default_data, f)

    @staticmethod
    def update_spawn(bot, boss, status, time):
        with open(bot.spawn_data_file, 'rb') as f:
            raw_data = marshal.load(f)

        row = raw_data[boss][status]
        if row and time < row[-1] + 300:
            # it has been less than 5m since the last recorded time... This should probbaly not be recorded
            raise RuntimeWarning
        row.append(time)
        raw_data[boss].update({status: row})
        with open(bot.spawn_data_file, 'wb') as f:
            marshal.dump(raw_data, f)
