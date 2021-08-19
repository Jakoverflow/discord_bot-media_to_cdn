import discord
import sqlite3
from discord.ext import commands
from datetime import datetime

prefix = '!'

# setup discord bot
client = commands.Bot(command_prefix=prefix)
client.remove_command('help')
client.embedcolor = 0x236187

# channels to check for messages (given as integer)
client.added_channels = []

# load in managechannel commands
client.load_extension('managechannels')


# called when bot is started
@client.event
async def on_ready():
    try:

        # fetching all added channel from database
        dbcon = sqlite3.connect("./database.sqlite")
        dbcrs = dbcon.cursor()
        dbcrs.execute('SELECT (channel_id) FROM channels')
        for channel in dbcrs.fetchall():
            client.added_channels.append(channel[0])

        dbcon.close()

    # if an error occurs while accessing the databse its printed and logged
    except sqlite3.Error as err:
        f = open("logs/log_%d-%d.txt" % (datetime.now().year, datetime.now().month), "a")
        content = "%s :: %s ::: %s\n" % (datetime.now().strftime("%Y-%m-%d/%H:%M:%S"), 'error database startup', err)
        print(content)
        f.write(content)
        f.flush()
        f.close()

    print(f"Logged in as {client.user.name}")


# called when a message is send
@client.event
async def on_message(msg):
    # skip if the message is send by a bot
    if msg.author.bot:
        return

    # all the magic
    # check if the message was send in an added channel
    if msg.channel.id in client.added_channels:

        # checks the message if it is a suitable url
        if 'media.discordapp.net' in msg.content and (msg.content.endswith('.mp4') or msg.content.endswith('.webm')):
            new_msg = msg.content.replace('media.discordapp.net', 'cdn.discordapp.com')

            # send new url and delete old one
            await msg.channel.send(new_msg)
            await msg.delete()

            # print to console for successfull url replacement
            print(f'{datetime.now().strftime("%Y-%m-%d/%H:%M:%S")} :: success url replaced :: {msg.guild.name} :: '
                  f'{msg.author} :: {msg.content}')

    # continue to process if a command is invoked
    await client.process_commands(msg)


@client.command(name='help')
async def helpinfos(ctx):
    await ctx.send(embed=discord.Embed(description='This Bot single purpose is to replace \n**media.discordapp.net** '
                                                   'video urls to **cdn.discordapp.com**\n\n'
                                                   'As Mod you can use the following commands:\n'
                                                   f'- `{client.command_prefix}addchannel [channel]` to add a channel where url\'s will be '
                                                   'replaced\n '
                                                   f'- `{client.command_prefix}removechannel [channel]` to remove a channel\n'
                                                   f'- `{client.command_prefix}listchannel` lists all channels where urls will are being replaced',
                                       color=client.embedcolor)\
        .set_image(url='https://media.discordapp.net/attachments/347254691966615552/866344332394364938/image0.gif') \
        .set_footer(
        text='You can find the code of the bot here: https://github.com/Jakoverflow/discord_bot-media_to_cdn'))

client.run('your discord token')
