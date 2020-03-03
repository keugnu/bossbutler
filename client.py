import datetime
import discord
from discord.ext import tasks, commands


class Client(discord.Client):
    def __init__(self):
        super().__init__()

        self.rcv_time = datetime.datetime(1, 1, 1)

    async def on_message(self, message):
        if not message.channel.name == 'world-boss-alerts':
            return
        if not message.mention_everyone:
            return
        if message.created_at < self.rcv_time + datetime.timedelta(minutes=30):
            return
        else:
            self.rcv_time = message.created_at
            guild = message.guild
            vc = await guild.create_voice_channel(name='wboss-encounter')
            members = discord.utils.get(guild.voice_channels, name='General').members
            for member in members:
                await member.move_to(vc)
