import logging

import discord
from discord.ext import commands


class Control(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log = logging.getLogger('bossbutler.cog.control')

    @commands.command()
    @commands.guild_only()
    async def stop(self, ctx):
        if ctx.voice_client:
            self.log.info(f'Leaving {ctx.voice_client.channel}.')
            await ctx.voice_client.disconnect()
        else:
            await ctx.send('I am not connected to any channels right now...')

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def play(self, ctx):
        self.log.info(f'Playing the alarm now.')
        ctx.voice_client.play(
            discord.FFmpegPCMAudio(
                self.bot.yt_file,
                executable=self.bot.ffmpeg,
            )
        )

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def join(self, ctx, channel: str):
        self.log.info(f'{ctx.message.author} asked me to move to {channel}.')
        if ctx.voice_client:
            self.log.warn(f'I am already connected to {ctx.voice_client.channel}, but I will move anyways.')
            await ctx.voice_client.disconnect()
        try:
            await discord.utils.get(ctx.guild.voice_channels, name=channel).connect()
        except Exception as e:
            self.log.exception(f'Cannot join {channel}: {e}')
            raise commands.CommandError(f'I am unable to join {channel}.')
