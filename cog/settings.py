import os
import logging

from discord.ext import commands

import utils


class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log = logging.getLogger('bossbutler.cog.settings')

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def alarm(self, ctx, link: str):
        self.log.debug(f'{ctx.author}:{ctx.command}:{ctx.message}')
        msg = f'Current alarm is: {self.bot.yt_title}. Changing to: {link}.'
        await ctx.send(msg)
        self.log.info(msg)
        await self._change_alarm(ctx, link)

    @commands.command(enabled=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def watch(self, ctx, name: str):
        self.log.debug(f'{ctx.author}:{ctx.command}:{ctx.message}')
        msg = f'Setting watch channel to: {name}.'
        await ctx.send(msg)
        self.log.info(msg)
        self.bot.watch = name.lower()

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def wakeup(self, ctx, name: str):
        self.log.debug(f'{ctx.author}:{ctx.command}:{ctx.message}')
        msg = f'Setting wakeup channel to: {name}.'
        await ctx.send(msg)
        self.log.info(msg)
        self.bot.wakeup = name.lower()

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def prefix(self, ctx, char: str):
        self.log.debug(f'{ctx.author}:{ctx.command}:{ctx.message}')
        if len(char) > 1:
            await ctx.send(f'Prefixes can only be one character.')
            self.log.warn(f'Attempted to change prefix to {char}. Prefix will remain as {self.box.prefix}.')
        else:
            msg = f'Changing command prefix to: {char}'
            await ctx.send(msg)
            self.log.info(msg)
            self.bot.command_prefix = char

    async def _change_alarm(self, ctx, link):
        self.log.debug(f'{ctx.author}:{ctx.command}:{ctx.message}')
        try:
            yt = self.bot.yt_file
            self.bot.yt_title, self.bot.yt_file = utils.download_yt(link)
            msg = f'Set alarm to: {self.bot.yt_title}'
            await ctx.send(msg)
            self.log.info(msg)
        except Exception:
            await ctx.send(f'There was an error trying to change the alarm so I am not be changing it right now.')
            self.log.exception('Alarm will not be changed.')
        try:
            self.log.info(f'Removing previous alarm: {yt}')
            os.remove(yt)
        except Exception:
            self.log.exception(f'Unable to remove previous file: {yt}')
