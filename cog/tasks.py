import asyncio
import datetime
import logging
import marshal

import discord
import pytz
from discord.ext import commands, tasks

import utils

DAY_MAP = {
    0: 'Monday',
    1: 'Tuesday',
    2: 'Wednesday',
    3: 'Thursday',
    4: 'Friday',
    5: 'Saturday',
    6: 'Sunday'
}


class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log = logging.getLogger('bossbutler.cog.tasks')
        self.lock = asyncio.Lock()
        self.tuesday_reset.start()
        self.death_integrity.start()
        self.commit_settings.start()
        self.check_windows.start()

    def cog_unload(self):
        self.log.warning('Stopping all tasks before quitting.')
        self.tuesday_reset.cancel()
        self.death_integrity.cancel()
        self.commit_settings.cancel()
        self.check_windows.cancel()

    @tasks.loop(count=1)
    async def tuesday_reset(self):
        """Overwrite last death to Tuesday 7AM PST"""
        self.log.debug('Running tuesday_reset.')
        now = datetime.datetime.now().astimezone(pytz.utc)
        self.log.debug(f'Now: {now}')
        next_reset = utils.next_server_reset()
        self.log.info('Today is Tuesday, after reset. Resetting all the last deaths.')

        async with self.lock:
            with open(self.bot.spawn_data_file, 'rb') as f:
                raw_data = marshal.load(f)

            for boss in raw_data.keys():
                for i in ['', '2']:
                    row = raw_data[boss]['down' + i][:-1] if raw_data[boss]['down' + i] else []
                    row.append(next_reset.timestamp())
                    self.log.debug(f'Updated for {boss}: {row}')
                    raw_data[boss].update({'down' + i: row})

            with open(self.bot.spawn_data_file, 'wb') as f:
                marshal.dump(raw_data, f)

        self.log.debug('Finished tuesday_reset.')
        self.tuesday_reset.restart()

    @tuesday_reset.before_loop
    async def wait_for_server_reset(self):
        next_reset = utils.next_server_reset()
        async with self.lock:
            with open(self.bot.spawn_data_file, 'rb') as f:
                raw_data = marshal.load(f)

        last_death = raw_data['azu']['down'][-1]
        if last_death == next_reset.timestamp():
            was_reset = True
        else:
            self.log.info('Looks like the deaths need to be reset.')
            was_reset = False

        return None if was_reset is False else await Tasks._wait_for_next_reset(next_reset)

    @tasks.loop(minutes=20)
    async def death_integrity(self):
        # WARNING - THIS TASK DOES NOT WORK FOR MULTIPLE REALMS
        self.log.debug('Running death_integrity.')
        msg = 'Death information is missing for {boss}'
        with open(self.bot.spawn_data_file, 'rb') as f:
            raw_data = marshal.load(f)

        for boss in raw_data.keys():
            if (
                    raw_data[boss].get('up') and len(raw_data[boss].get('up')) > len(raw_data[boss].get('down')) or
                    raw_data[boss].get('up2') and len(raw_data[boss].get('up2')) > len(raw_data[boss].get('down2'))
            ):
                self.log.warning(f'{boss} death data might be missing!')
                self.log.debug(f'up: {raw_data[boss].get("up")}   down: {raw_data[boss].get("down")}')
                self.log.debug(f'up2: {raw_data[boss].get("up2")}   down2: {raw_data[boss].get("down2")}')
                ch = discord.utils.find(
                    lambda i: i.name == 'bot-test' and i.guild.name == "keugnu's server",
                    self.bot.get_all_channels()
                )
                await ch.send(msg.format(boss=boss))
        self.log.debug('Finished death_integrity.')

    @tasks.loop(minutes=10)
    async def commit_settings(self):
        self.log.debug('Running commit_settings.')
        try:
            with open(self.bot.settings_file, 'wb') as f:
                marshal.dump(self.bot.settings, f)
        except (FileNotFoundError, TypeError):
            self.log.error('Settings file does not exist')
        except OSError as e:
            self.log.error(f'Looks like {self.bot.settings_file} is inaccessible right now: {e}')

        self.log.debug('Finished commit_settings.')

    @tasks.loop(hours=2)
    async def check_windows(self):
        self.log.debug('Running check_windows')
        try:
            with open(self.bot.spawn_data_file, 'rb') as f:
                raw_data = marshal.load(f)
        except (FileNotFoundError, TypeError):
            self.log.error(f'Spawn data file does not exist at {self.bot.spawn_data_file}')
        else:
            windows = []
            for boss, statuses in raw_data.items():
                if statuses.get('down') and not len(statuses.get('up')) > len(statuses.get('down')):
                    windows.append((boss, self.bot._calculate_window(statuses.get('down')[-1])))
                if statuses.get('down2') and not len(statuses.get('up2')) > len(statuses.get('down2')):
                    windows.append((boss, self.bot._calculate_window(statuses.get('down2')[-1])))

            self.log.info(f'Next windows are {" | ".join("{} {}".format(k, v) for k, v in windows)}')
            now = datetime.datetime.now(pytz.timezone('US/Eastern'))

            for boss, window in windows:
                if window.timestamp() < now.timestamp() + 3600 * 2:
                    self.log.info(f'{window} opens soon. now: {now}')
                    remaining = window.timestamp() - now.timestamp()
                    if remaining > 0:
                        msg = f'A window for {boss.upper()} is opens in {int(remaining / 3600)}h{int(remaining % 60)}m! It opens at {window.strftime("%H:%M %Z")}.'
                    elif remaining <= -3600 * 2:
                        msg = f'A window for {boss.upper()} is open NOW!'
                    ch = discord.utils.find(
                        lambda i: i.name == 'bot-test' and i.guild.name == "keugnu's server",
                        self.bot.get_all_channels()
                    )
                    await ch.send(msg)

        self.log.debug('Finished check_windows')

    @staticmethod
    async def _wait_for_next_reset(next_reset):
        log = logging.getLogger('bossbutler.cog.tasks')
        while datetime.datetime.now().astimezone(pytz.utc) > next_reset:
            wait_for = (next_reset - datetime.datetime.now().astimezone(pytz.utc)).total_seconds()
            if abs(wait_for) < 11 * 3600:   # wait for at least 11 hours
                wait_for = 11 * 3600
            log.debug(f'Waiting for {abs(wait_for)} seconds to check for server reset again.')
            await asyncio.sleep(abs(wait_for) if wait_for < 86400 else 86400)
