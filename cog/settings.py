import os
import logging

import discord
from discord.ext import commands

import utils


async def valid_channel(ctx, name):
    ch = ' '.join(name)
    try:
        assert discord.utils.get(ctx.guild.channels, name=ch)
    except AssertionError:
        await ctx.send(f"{ch} doesn't seem to be a valid channel in this server. Check the name and try again.")
        raise commands.CommandError(f'{ch} is not a valid channel name.')
    return ch

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log = logging.getLogger('bossbutler.cog.settings')

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def alarm(self, ctx, link: str):
        """Sets the alarm sound :: !alarm <YouTube link>"""
        self.log.debug(f'{ctx.author}:{ctx.command}:{ctx.message}')
        msg = f'Current alarm is: {self.bot.yt_title}. Changing to: {link}.'
        await ctx.send(msg)
        self.log.info(msg)
        await self._change_alarm(ctx, link)

    # this could be used if we want the bot to just watch a channel for keywords
    @commands.command(enabled=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def watch(self, ctx, *name: str):
        """Changes which channel BossButler will watch for keywords"""
        self.log.debug(f'{ctx.author}:{ctx.command}:{ctx.message}')
        ch = await valid_channel(ctx, name)
        msg = f'Setting watch channel to: {ch}.'
        await ctx.send(msg)
        self.log.info(msg)
        self.bot.watch = ch

    @commands.command(name='voice-channel', aliases=['vc'])
    @commands.guild_only()
    async def voice_channel(self, ctx, *name):
        """Changes the channel that BossButler will enter automatically and play the alert"""
        self.log.debug(f'{ctx.author}:{ctx.command}:{ctx.message}')
        ch = await valid_channel(ctx, name)
        msg = f'Setting wakeup channel to: {ch}.'
        await ctx.send(msg)
        self.log.info(msg)
        self.bot.wakeup = ch

    @commands.command()
    @commands.guild_only()
    async def prefix(self, ctx, char: str):
        """Changes the command prefix for BossButler"""
        self.log.debug(f'{ctx.author}:{ctx.command}:{ctx.message}')
        if len(char) > 1:
            await ctx.send(f'Prefixes can only be one character.')
            self.log.warn(f'Attempted to change prefix to {char}. Prefix will remain as {self.box.prefix}.')
        else:
            msg = f'Changing command prefix to: {char}'
            await ctx.send(msg)
            self.log.info(msg)
            self.bot.command_prefix = char

    @commands.command(name='announce-channel', aliases=['ac'])
    async def text_announcements(self, ctx, *name):
        """Changes which channel BossButler will use to post announcements"""
        self.log.debug(f'{ctx.author}:{ctx.command}:{ctx.message}')
        ch = await valid_channel(ctx, name)
        await ctx.send(f'Setting the channel for announcements to {ch}.')
        self.bot.announcements = ch

    async def _change_alarm(self, ctx, link):
        self.log.debug(f'{ctx.author}:{ctx.command}:{ctx.message}')
        try:
            yt = self.bot.yt_file
            self.bot.yt_url, self.bot.yt_title, self.bot.yt_file = utils.download_yt(link)
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
