import datetime
import logging
import marshal
from collections import defaultdict

import discord
import pytz
from discord.ext import commands


class Info(commands.Cog):

    BOSS_NAMES = {
        'azu': 'Azurgos',
        'kazz': 'Lord Kazzak',
        'green': 'Dragons of Nightmare',
    }

    def __init__(self, bot):
        self.bot = bot
        self.log = logging.getLogger('bossbutler.cog.info')

    @commands.command(aliases=['w'])
    async def windows(self, ctx):
        now = datetime.datetime.now().astimezone(pytz.timezone('US/Eastern'))

        with open(self.bot.spawn_data_file, 'rb') as f:
            raw_data = marshal.load(f)

        windows = defaultdict()
        for boss, statuses in raw_data.items():
            if statuses.get('down'):
                windows.update({boss: [self.bot._calculate_window(statuses.get('down')[-1])]})
            if statuses.get('down2'):
                windows[boss].append(self.bot._calculate_window(statuses.get('down2')[-1]))

        resp = discord.Embed(
            title='Current World Boss Spawn Windows',
            description='Windows open 72 hours after the last kill and 12 hours after the weekly server reset.\nThe next windows are:')
        resp.set_author(name='BossButler', icon_url=ctx.bot.user.avatar_url)

        for boss in windows.keys():
            for i, window in enumerate(windows[boss]):
                if window < now:
                    windows[boss][i] = 'NOW!'

            times = '\n'.join([w.strftime('%b %d %H:%M %Z') if isinstance(w, datetime.datetime) else w for w in windows[boss]])

            resp.add_field(
                name=Info.BOSS_NAMES.get(boss),
                value=times,
            )

        await ctx.send(embed=resp)
