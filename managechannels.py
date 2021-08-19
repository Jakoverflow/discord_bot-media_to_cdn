import discord
import os
import sqlite3
from discord.ext import commands
from datetime import datetime

# add mod access only


class ManageChannels(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.embedcolor = client.embedcolor
        self.added_channels = client.added_channels
        self.pref = client.command_prefix

    def writelog(self, ctx, entry):
        content = "%s :: %s" % (datetime.now().strftime("%Y-%m-%d/%H:%M:%S"), entry)
        print(content)
        try:
            f = open("logs/log_%s_%d-%d.txt" % (ctx.guild.name, datetime.now().year, datetime.now().month), "a")
            f.write(content)
            f.flush()
            f.close()
        except FileNotFoundError as err:
            print("%s :: error writelog :: FileNotFoundError :: %s" % (datetime.now().strftime("%Y-%m-%d/%H:%M:%S"), err))
            os.makedirs('logs')

    @commands.command(name='addchannel')
    async def addchannel(self, ctx, channel: discord.TextChannel):
        # check if a channel is already added
        if channel.id in self.added_channels:
            try:
                await ctx.send(
                    embed=discord.Embed(
                        description='The Channel %s is **already added**.\n\nYou can remove a channel with '
                                    '`%sremovechannel [channel]`' % (channel.mention, self.pref),
                        title='Already added', color=self.embedcolor))

            except discord.ext.commands.errors as err:
                self.writelog(ctx, f'error discord add already added :: {ctx.author} :: {channel.id} : {channel} ::: {err}')
                await ctx.channel.send(embed=discord.Embed(title='discord error', description=err))

            else:
                self.writelog(ctx, f'success add already added :: {ctx.author} :: {channel.id} : {channel}')

        # if channel is not added start adding it
        else:
            try:
                dbcon = sqlite3.connect("./database.sqlite")
                dbcrs = dbcon.cursor()

                dbcrs.execute("INSERT INTO channels (channel_id, server_id) VALUES (?, ?)", (channel.id, ctx.guild.id))
                dbcon.commit()
                dbcon.close()

                self.added_channels.append(channel.id)

                await ctx.send(
                    embed=discord.Embed(description='New channel:%s\nAdded to replace **media.discordapp.net** video '
                                                    'urls to **cdn.discord.com**.\n\n'
                                                    f'To remove a channel use `{self.pref}removechannel [channel]`'
                                                    % channel.mention, title='Added', color=self.embedcolor))
            except sqlite3.Error as err:
                self.writelog(ctx, f'error database add :: {ctx.author} :: {channel.id} : {channel} ::: {err}')
                await ctx.channel.send(embed=discord.Embed(title='databse error', description=err))
                raise err

            except discord.ext.commands.errors as err:
                self.writelog(ctx, f'error discord add :: {ctx.author} :: {channel.id} : {channel} ::: {err}')
                await ctx.channel.send(embed=discord.Embed(title='discord error', description=err))
                raise err

            else:
                self.writelog(ctx, f'success add :: {ctx.author} :: {channel.id} : {channel}')

    @commands.command(name='removechannel')
    async def removechannel(self, ctx, channel: discord.TextChannel):
        # check if channel is added
        if channel.id in self.added_channels:
            try:
                dbcon = sqlite3.connect("./database.sqlite")
                dbcrs = dbcon.cursor()
                dbcrs.execute("DELETE FROM channels WHERE channel_id = (?)", (channel.id,))
                dbcon.commit()
                dbcon.close()

                self.added_channels.remove(channel.id)

                await ctx.send(
                    embed=discord.Embed(description='Video urls in channel %s will **no longer** be replaced.\n\n'
                                                    f'You can add other channel with `{self.pref}addchannel [channel]`.'
                                                    % channel.mention, title='Removed', color=self.embedcolor))
            except sqlite3.Error as err:
                self.writelog(ctx, f'error database remove :: {ctx.author} :: {channel.id} : {channel} ::: {err}')
                await ctx.channel.send(embed=discord.Embed(title='databse error', description=err))
                raise err

            except discord.ext.commands.errors as err:
                self.writelog(ctx, f'error discord remove :: {ctx.author} :: {channel.id} : {channel} ::: {err}')
                await ctx.channel.send(embed=discord.Embed(title='discord error', description=err))
                raise err

            else:
                self.writelog(ctx, f'success remove :: {ctx.author} :: {channel.id} : {channel}')

        # if channel not already added
        else:
            try:
                await ctx.send(
                    embed=discord.Embed(description='Channel %s is **not added**.\n\nYou can add a channel with '
                                                    '`%saddchannel [channel]`.' % (channel.mention, self.pref),
                                        title='Not added', color=self.embedcolor))

            except discord.ext.commands.errors as err:
                self.writelog(ctx, f'error discord removed not added :: {ctx.author} :: {channel.id} : {channel} ::: {err}')
                await ctx.channel.send(embed=discord.Embed(title='discord error', description=err))
                raise err

            else:
                self.writelog(ctx, f'success removed not added :: {ctx.author} :: {channel.id} : {channel}')

    @commands.command(name='listchannel')
    async def listchannel(self, ctx):
        try:
            # database request fetch all channel_id's from the current server
            dbcon = sqlite3.connect("./database.sqlite")
            dbcrs = dbcon.cursor()
            dbcrs.execute("SELECT channel_id FROM channels WHERE server_id=(?)", (ctx.guild.id,))
            dbitems = dbcrs.fetchall()
            dbcon.close()

            if not dbitems:
                await ctx.send(embed=discord.Embed(title='No channels added.',
                                                   description=f"Use `{self.pref}addchannel` to add a channel to replace urls.",
                                                   color=self.embedcolor))
                return

            description = ''
            for item in dbitems:
                channel = self.client.get_channel(item[0])
                description += '- %s\n' % channel.mention

            # send messages with a list of channels
            await ctx.send(embed=discord.Embed(title="Listed below are all added channels:", description=description,
                                               colour=self.embedcolor))

        except sqlite3.Error as err:
            self.writelog(ctx, f'error database list :: {ctx.author} ::: {err}')
            await ctx.channel.send(embed=discord.Embed(title='databse error', description=err))
            raise err

        except discord.ext.commands.errors as err:
            self.writelog(ctx, f'error discord list :: {ctx.author} ::: {err}')
            await ctx.channel.send(embed=discord.Embed(title='discord error', description=err))
            raise err

        else:
            self.writelog(ctx, f'success list :: {ctx.author}')

    @addchannel.error
    async def addchannel_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.channel.send(embed=discord.Embed(description='Plase add a channel like\n'
                                                                   f'`{self.pref}addchannel test-channel`',
                                                       title='Missing Channel', color=self.embedcolor))

        elif isinstance(error, commands.ChannelNotFound):
            await ctx.channel.send(embed=discord.Embed(description='There was no channel found for **%s**\n\n'
                                                                   'Try again by pinging the channel:\nuse a **#** '
                                                                   'before writing the channel for example:\n'
                                                                   '`#test-channel`' % error.argument,
                                                       title='Channel not Found', color=self.embedcolor))

        else:
            raise error

    @removechannel.error
    async def addchannel_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.channel.send(embed=discord.Embed(description='Plase add a channel like\n'
                                                                   f'`{self.pref}removechannel test-channel`\n\n'
                                                                   f'Use `{self.pref}listchannel` to see which channel are added',
                                                       title='Missing Channel', color=self.embedcolor))

        elif isinstance(error, commands.ChannelNotFound):
            await ctx.channel.send(embed=discord.Embed(description='There was no channel found for **%s**\n\n'
                                                                   'Try again by pinging the channel:\nuse a **#** '
                                                                   'before writing the channel for example:\n'
                                                                   '`#test-channel`' % error.argument,
                                                       title='Channel not Found', color=self.embedcolor))

        else:
            raise error


def setup(client):
    client.add_cog(ManageChannels(client))
