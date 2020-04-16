import logging

import discord
from discord.ext import commands


class Alerts(commands.Cog):

    UP_STATUSES = ['up', 'spawned']
    DOWN_STATUES = ['down', 'dead']

    def __init__(self, bot):
        self.bot = bot
        self.log = logging.getLogger('bossbutler.cog.alerts')

    def validate_status(self, status):
        if status:
            assert status in Alerts.UP_STATUSES or status in Alerts.DOWN_STATUES

    async def _start_alarm(self, ctx):
        self.log.info(f'Joining voice channel "{self.bot.wakeup}..."')
        vc = await discord.utils.get(ctx.guild.voice_channels, name=self.bot.wakeup).connect()
        self.log.info(f'Begining to play alarm: "{self.bot.yt_file}"')
        vc.play(discord.FFmpegPCMAudio(self.bot.yt_file, executable=self.bot.ffmpeg))

    async def _stop_alarm(self, ctx):
        await self.bot.get_command('stop').invoke(ctx)

    async def action(self, ctx, status):
        try:
            self.validate_status(status)
        except AssertionError:
            msg = f'{status} is an invalid option. You must use one of: {", ".join(Alerts.STATUSES)}'
            await ctx.send(msg)
            raise commands.CommandError(msg)
        if status in Alerts.UP_STATUSES:
            await self._start_alarm(ctx)
        elif status in Alerts.DOWN_STATUES:
            await self._stop_alarm(ctx)

    # The boss-specific commands are meant for tracking timers and windows. This functionality is not yet in place.
    # We can track the timers and windows in DDB, perhaps.
    @commands.command(
        aliases=['azuregos', 'az'],
        usage=f'azu <status> <whisper targets> :: !azu up manbearpig saitama',
        enabled=False,
    )
    async def azu(self, ctx, status, *names):
        status = status.lower()
        self.log.info(f'Azuregos is {status}!')
        await self.action(ctx, status)

    @commands.command(
        aliases=['kazzak', 'kaz'],
        usage=f'kazz <status> <whisper targets> :: !kazz up manbearpig saitama',
        enabled=False,
    )
    async def kazz(self, ctx, status, *names):
        status = status.lower()
        self.log.info(f'Kazzak is {status}!')
        await self.action(ctx, status)

    @commands.command(
        aliases=['emeriss'],
        usage=f'emer <status> <whisper targets> :: !emer up manbearpig saitama',
        enabled=False,
    )
    async def emer(self, ctx, status, *names):
        status = status.lower()
        self.log.info(f'Emeriss is {status}!')
        await self.action(ctx, status)

    @commands.command(
        aliases=['lethon'],
        usage=f'leth <status> <whisper targets> :: !leth up manbearpig saitama',
        enabled=False,
    )
    async def leth(self, ctx, status, *names):
        status = status.lower()
        self.log.info(f'Lethon is {status}!')
        await self.action(ctx, status)

    @commands.command(
        aliases=['taerar'],
        usage=f'taer <status> <whisper targets> :: !taer up manbearpig saitama',
        enabled=False,
    )
    async def taer(self, ctx, status, *names):
        status = status.lower()
        self.log.info(f'Taerar is {status}!')
        await self.action(ctx, status)

    @commands.command(
        aliases=['ysondre'],
        usage=f'yson <status> <whisper targets> :: !yson up manbearpig saitama',
        enabled=False,
    )
    async def yson(self, ctx, status, *names):
        status = status.lower()
        self.log.info(f'Ysondre is {status}!')
        await self.action(ctx, status)

    @commands.command()
    async def up(self, ctx):
        self.log.info(f'{ctx.author.name} says a boss is up!')
        if not self.bot.wakeup:
            await ctx.send(f'The wakeup channel is not set. Please set it with {self.bot.command_prefix}wakeup.')
            raise commands.CommandError(f'The wakeup channel is not set. Please set it with {self.bot.command_prefix}wakeup.')
        await self._start_alarm(ctx)