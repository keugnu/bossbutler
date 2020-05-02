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
    @commands.cooldown(rate=1, per=120)
    async def alarm(self, ctx, link: str):
        """Sets the alarm sound :: !alarm <YouTube link>"""
        self.log.debug(f'{ctx.author}:{ctx.command}:{ctx.message}')
        msg = f'Current alarm is: {self.bot.settings[ctx.guild.id].get("yt_title")}. Changing to: {link}.'
        await ctx.send(msg)
        self.log.info(msg)
        await self._change_alarm(ctx, link)

    @commands.command(enabled=False)
    @commands.guild_only()
    async def watch(self, ctx, *name: str):
        """Changes which channel BossButler will watch for keywords"""
        self.log.debug(f'{ctx.author}:{ctx.command}:{ctx.message}')
        ch = await valid_channel(ctx, name)
        msg = f'Setting watch channel to: {ch}.'
        await ctx.send(msg)
        self.log.info(msg)
        self.bot.settings[ctx.guild.id].update({'watch': ch})

    @commands.command(name='voice-channel', aliases=['vc'])
    @commands.guild_only()
    async def voice_channel(self, ctx, *name):
        """Changes the channel that BossButler will enter automatically and play the alert"""
        self.log.debug(f'{ctx.author}:{ctx.command}:{ctx.message}')
        ch = await valid_channel(ctx, name)
        msg = f'Setting wakeup channel to: {ch}.'
        await ctx.send(msg)
        self.log.info(msg)
        self.bot.settings[ctx.guild.id].update({'wakeup': ch})

    @commands.command(name='announce-channel', aliases=['ac'])
    async def text_announcements(self, ctx, *name):
        """Changes which channel BossButler will use to post announcements"""
        self.log.debug(f'{ctx.author}:{ctx.command}:{ctx.message}')
        ch = await valid_channel(ctx, name)
        await ctx.send(f'Setting the channel for announcements to {ch}.')
        self.bot.settings[ctx.guild.id].update({'announcements': ch})

    async def _change_alarm(self, ctx, link):
        self.log.debug(f'{ctx.author}:{ctx.command}:{ctx.message}')
        try:
            yt = self.bot.settings.get('yt_file')
            url, title, path = utils.download_yt(link)
            self.bot.settings[ctx.guild.id].update(
                {
                    'yt_url': url,
                    'yt_title': title,
                    'yt_file': path
                }
            )
            msg = f'Set alarm to: {title}'
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
