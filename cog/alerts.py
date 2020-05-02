import logging

import discord
import pytz

from discord.ext import commands


class Alerts(commands.Cog):

    UP_STATUSES = ['up', 'spawn', 'spawned']
    DOWN_STATUES = ['down', 'dead']

    def __init__(self, bot):
        self.bot = bot
        self.log = logging.getLogger('bossbutler.cog.alerts')

    async def _start_alarm(self, ctx):
        if not self.bot.settings[ctx.guild.id].get('wakeup'):
            await ctx.send(f"I don't know which channel to join! Please set it with {self.bot.command_prefix}wakeup.")
            raise commands.CommandError('Wakeup channel not set.')
        if not self.bot.settings[ctx.guild.id].get('announcements'):
            await ctx.send(f"I don't know which channel to notify! Please set it with {self.bot.command_prefix}announce-channel.")
        ch_announce = discord.utils.get(ctx.guild.channels, name=self.bot.settings[ctx.guild.id].get('announcements'))
        await ch_announce.send(f'@here {ctx.author.nick or ctx.author.name} says a boss is up!')
        self.log.info(f'Joining voice channel {self.bot.settings[ctx.guild.id].get("wakeup")}.')
        vc = await discord.utils.get(ctx.guild.voice_channels, name=self.bot.settings[ctx.guild.id].get('wakeup')).connect()
        self.log.info(f'Begining to play alarm: {self.bot.settings[ctx.guild.id].get("yt_file")}')
        vc.play(discord.FFmpegPCMAudio(self.bot.settings[ctx.guild.id].get('yt_file'), executable=self.bot.ffmpeg))

    async def _stop_alarm(self, ctx):
        await ctx.send(f'Stopping the alarms now!')
        await self.bot.get_command('stop').invoke(ctx)

    async def action(self, ctx, boss, status):
        time = ctx.message.created_at.astimezone(pytz.utc).timestamp()
        if status in Alerts.UP_STATUSES:
            try:
                self.bot.update_spawn(self.bot, boss, 'up', time)
            except RuntimeWarning:
                await ctx.send(
                    'It has been less than 5 minutes since the last time this boss was reported up.'
                    f'I think there has been a mistake. If not, use {self.bot.command_prefix}up instead.'
                )
            await self._start_alarm(ctx)
        elif status in Alerts.DOWN_STATUES:
            self.bot.update_spawn(self.bot, boss, 'down', time)
            await self._stop_alarm(ctx)
        else:
            msg = f'{status} is an invalid option. You must use one of: {", ".join([Alerts.UP_STATUSES, Alerts.DOWN_STATUES])}'
            await ctx.send(msg)
            raise commands.CommandError(msg)

    @commands.command(
        aliases=['azuregos', 'az'],
    )
    async def azu(self, ctx, status, *names):
        """azu <status> <whisper targets> :: !azu up manbearpig saitama"""
        self.log.debug(f'{ctx.author}:{ctx.command}:{ctx.message}')
        status = status.lower()
        self.log.info(f'Azuregos is {status}!')
        await self.action(ctx, 'azu', status)

    @commands.command(
        aliases=['kazzak', 'kaz'],
    )
    async def kazz(self, ctx, status, *names):
        """!kazz <status> <whisper targets> :: !kazz up manbearpig saitama"""
        self.log.debug(f'{ctx.author}:{ctx.command}:{ctx.message}')
        status = status.lower()
        self.log.info(f'Kazzak is {status}!')
        await self.action(ctx, 'kazz', status)

    @commands.command()
    async def greenies(self, ctx, status):
        """!greenies <status> <whisper targets> :: !greenies up manbearpig saitama"""
        self.log.debug(f'{ctx.author}:{ctx.command}:{ctx.message}')
        status = status.lower()
        self.log.info(f'Green dragons are {status}!')
        await self.action(ctx, 'green', status)

    @commands.command()
    async def up(self, ctx):
        self.log.debug(f'{ctx.author}:{ctx.command}:{ctx.message}')
        self.log.info(f'{ctx.author.nick or ctx.author.name} says a boss is up!')
        if not self.bot.settings[ctx.guild.id].get('wakeup'):
            msg = f'The wakeup channel is not set. Please set it with {self.bot.command_prefix}voice-channel.'
            await ctx.send(msg)
            raise commands.CommandError(msg)
        await self._start_alarm(ctx)

    @commands.command()
    async def whisper(self, ctx, *names):
        """Sends an annoucement to whisper <names> :: !whisper saitama manbearpig"""
        self.log.debug(f'{ctx.author}:{ctx.command}:{ctx.message}')
        self.log.info(f'{ctx.author.nick} says to whisper {", ".join(names)} for invites.')
        channel = discord.utils.get(ctx.guild.channels, name=self.bot.settings[ctx.guild.id].get('announcements'))
        await channel.send(f'@here Whisper {", ".join(names)} for invites!')
