from discord.ext import commands
from datetime import datetime

# setup discord bot
client = commands.Bot(command_prefix='!')

# channels to check for messages (given as integer)
channels = []


# called when bot is started
@client.event
async def on_ready():
    print(f"Logged in as {client.user.name}")


# called when a message is send
@client.event
async def on_message(msg):
    if msg.author.bot:
        return

    if msg.channel.id in channels:
        if 'media.discordapp.net' in msg.content and (msg.content.endswith('.mp4') or msg.content.endswith('.webm')):
            print(f'{datetime.now().strftime("%Y-%m-%d/%H:%M:%S")}::{msg.author}::{msg.content}')
            new_msg = msg.content.replace('media.discordapp.net', 'cdn.discordapp.com')
            await msg.channel.send(new_msg)
            await msg.delete()

    await client.process_commands(msg)

client.run('your discord token')
