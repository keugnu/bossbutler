import os
from dotenv import load_dotenv

from discord.ext import tasks

from client import Client

def find(path, name):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)


dotenv_path = find(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)
token = os.getenv('DISCORD_TOKEN')
client = Client()


@tasks.loop(seconds=30)
async def check_channel():
    await client.wait_until_ready()
    for guild in client.guilds:
        for channel in guild.voice_channels:
            vc = channel if channel.name == 'wboss-encounter' else None
        if vc and not vc.members:
            await vc.delete()


check_channel.start()
client.run(token)
