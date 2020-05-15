import datetime
import os
import marshal
import shutil

import pytz
from discord.ext import commands

import utils
from cog import alerts, settings, control, tasks, info, errors


class Bot(commands.Bot):
    def __init__(self, pfx, debug=False):
        super().__init__(command_prefix=pfx)

        self.debug = debug
        self.settings = None
        self.ffmpeg = shutil.which('ffmpeg')
        self.settings_file = utils.find(os.path.dirname(__file__), 'settings-debug.bin' if debug is True else 'settings.bin')
        self.spawn_data_file = utils.find(os.path.dirname(__file__), 'spawn_data-debug.bin' if debug is True else 'spawn_data.bin')

        assert os.path.exists(self.ffmpeg)

    @staticmethod
    def add_cogs(bot):
        any(map(bot.add_cog, (alerts.Alerts(bot), settings.Settings(bot), control.Control(bot), info.Info(bot), errors.ErrorHandler(bot))))

    @staticmethod
    def start_tasks(bot):
        bot.add_cog(tasks.Tasks(bot))

    @staticmethod
    def init_spawn_data(bot):
        try:
            with open(bot.spawn_data_file, 'rb') as f:
                pass
        except (FileNotFoundError, TypeError):
            bot.spawn_data_file = os.path.join(os.path.dirname(__file__), 'spawn_data-debug.bin' if bot.debug is True else 'spawn_data.bin')

            with open(bot.spawn_data_file, 'wb') as f:
                default_data = {
                    'azu': {
                        'up': [],
                        'down': [],
                    },
                    'kazz': {
                        'up': [],
                        'down': [],
                    },
                    'green': {
                        'up': [],
                        'down': [],
                    }
                }
                marshal.dump(default_data, f)

    @staticmethod
    async def bootstrap_settings(bot):
        bot.settings_file = os.path.join(os.path.dirname(__file__), 'settings-debug.bin' if bot.debug is True else 'settings.bin')
        if not os.path.exists(bot.settings_file):
            with open(bot.settings_file, 'wb') as f:
                marshal.dump({}, f)

        with open(bot.settings_file, 'rb') as f:
            settings = marshal.load(f)

        async for guild in bot.fetch_guilds():
            if not settings.get(guild.id):
                settings.update({guild.id: {}})
            settings = bot.check_yt(guild.id, settings)

        with open(bot.settings_file, 'wb') as f:
            marshal.dump(settings, f)

        bot.settings = settings

    @staticmethod
    def check_yt(id, settings):
        try:
            with open(settings.get(id).get('yt_file')):
                pass
        except (FileNotFoundError, TypeError):
            url, title, path = utils.download_yt()
            settings[id].update(
                {
                    'yt_url': url,
                    'yt_title': title,
                    'yt_file': path
                }
            )

        return settings

    @staticmethod
    def update_spawn(bot, boss, status, time):
        with open(bot.spawn_data_file, 'rb') as f:
            raw_data = marshal.load(f)

        row = raw_data[boss][status]
        row.append(time)
        raw_data[boss].update({status: row})
        with open(bot.spawn_data_file, 'wb') as f:
            marshal.dump(raw_data, f)

    @staticmethod
    def _calculate_window(time):
        last_death = datetime.datetime.fromtimestamp(time).replace(tzinfo=pytz.utc)
        tues_reset = utils.next_server_reset()
        last_reset = tues_reset - datetime.timedelta(7)

        if last_reset >= last_death:
            window = last_reset + datetime.timedelta(hours=12)
        elif last_death + datetime.timedelta(3) < tues_reset:
            window = last_death + datetime.timedelta(3)
        else:
            window = tues_reset + datetime.timedelta(hours=12)

        return window.astimezone(pytz.timezone('US/Eastern'))
