import logging
import sys

import discord
from discord.ext import commands


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log = logging.getLogger('bossbutler.cog')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, err):
        if isinstance(err, (commands.CommandNotFound, commands.UserInputError)):
            await ctx.send(f"I can't find that command... Please use {self.bot.command_prefix}help to look at the avialable commands and try again.")

        elif isinstance(err, commands.DisabledCommand):
            await ctx.send(f'The {ctx.command.name} command is disabled right now.')

        elif isinstance(err, commands.CommandOnCooldown):
            await ctx.send(f'The {ctx.command.name} command is on cooldown. Try again later.')

        else:
            self.log.error(f'There was an error when calling {ctx.command}')
            await ctx.send('Something went wrong and I have logged the error for later investigation. Please reach out to keugnu for help.')

        self.log.error(err, exc_info=err.original if hasattr(err, 'original') else err)
