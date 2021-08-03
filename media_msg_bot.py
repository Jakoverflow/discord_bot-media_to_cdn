import discord
from discord.ext import commands

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
        if 'media.discordapp.net' in msg.content and msg.content.endswith('.mp4'):
            new_msg = msg.content.replace('media.discordapp.net', 'cdn.discordapp.com')
            await msg.channel.send(new_msg)
            await msg.delete()

    await client.process_commands(msg)


@client.command()
async def archivpins(ctx, thread: discord.Thread):
    channel = client.get_channel(ctx.channel.id)
    pins = await channel.pins()
    for msg in pins:

        msgstr = '\n**%s**: [%s](%s)' % \
                 (msg.author.name, msg.created_at.strftime('%H:%M %d-%B-%Y'), msg.jump_url)
        await thread.send(embed=discord.Embed(description=msgstr, colour=0xFFFFFF))
        await thread.send(msg.content)

client.run('your discord token')
