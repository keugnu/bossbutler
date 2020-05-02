import asyncio
import datetime
import logging
import marshal

import discord
import pytz
from discord.ext import commands, tasks


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
        self.was_reset_today = False
        self.tuesday_reset.start()
        self.death_integrity.start()

    @tasks.loop(minutes=60)
    async def tuesday_reset(self):
        """Overwrite last death to Tuesday 8AM PST"""
        self.log = logging.getLogger('bossbutler.tasks')
        self.log.info('Running Tuesday reset task...')
        self.lock = asyncio.Lock()
        today = datetime.datetime.today().astimezone(pytz.utc)
        self.log.debug(today)
        self.was_reset_today = False if today.weekday() == 2 else True
        if not self.was_reset_today and today.weekday() == 1 and today.hour > 16:
            self.was_reset_today = True
            self.log.info('Today is Tuesday, after reset. Resetting the last death.')
            reset_datetime = datetime.datetime(today.year, today.month, today.day, hour=16)
            async with self.lock:
                with open(self.bot.spawn_data_file, 'rb') as f:
                    raw_data = marshal.load(f)
                
                for boss, _ in raw_data.items():
                    row = raw_data[boss]['down'][:-1] if raw_data[boss]['down'] else []
                    row.append(reset_datetime.timestamp())
                    self.log.debug(f'Updated for {boss}: {row}')
                    raw_data[boss].update({'down': row})

                with open(self.bot.spawn_data_file, 'wb') as f:
                    marshal.dump(raw_data, f)
        else:
            self.log.info(f'Not time for a reset. Today is {DAY_MAP[today.weekday()]}.')
        self.log.info('Finished Tuesday reset task.')

    @tasks.loop(minutes=20)
    async def death_integrity(self):
        msg = '@here Death information is missing for {boss}'
        with open(self.bot.spawn_data_file, 'rb') as f:
            raw_data = marshal.load(f)

        for boss in raw_data.keys():
            if boss.get('up') and len(boss.get('up')) >= len(boss.get('down')):
                # TODO: Change somehow so that the bot can be active in multiple servers
                ch = discord.utils.get(
                    self.bot.get_all_channels(),
                    guild_name='World Boss',
                    name=self.bot.leadership_channel if self.bot.leadership_channel else self.bot.announcements
                )
                await ch.send(msg.format(boss=boss))
