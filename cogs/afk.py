import discord
from discord.ext import commands
from .utils.dataIO import fileIO
import os
import random
from .utils import checks


class Afk:
    """Server Based Afk Command"""
    def __init__(self, bot):
        self.bot = bot
        self.afk_data = 'data/afk/afk.json'
        self.settings = fileIO("data/afk/afk.json", "load")
    async def listener(self, message):
        tmp = {}
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        server = message.server
        db = fileIO(self.afk_data, 'load')
        if message.author.mention in db[server.id] and not message.content.startswith("r!!afk"):
            del db[server.id][message.author.mention]
            msg = discord.Embed(description='**{}, I automatically removed your afk status!**'.format(message.author.name), colour=discord.Colour(value=colour))
            await self.bot.send_message(message.channel, embed=msg)
            fileIO(self.afk_data, 'save', db)
        else:
            for mention in message.mentions:
                tmp[mention] = True
            if message.author.id != self.bot.user.id:
                data = fileIO(self.afk_data, 'load')
                for user in tmp:
                    if user.mention in data[message.server.id]:
                        if data[server.id][mention.mention]['MESSAGE'] is False:
                            msg = discord.Embed(description='**{} is currently afk.**'.format(mention.name), colour=discord.Colour(value=colour))
                        else:
                            msg = discord.Embed(description='**{} is currently afk.\nReason: {}**'.format(mention.name, data[message.server.id][mention.mention]['MESSAGE']), colour=discord.Colour(value=colour))
                        await self.bot.send_message(message.channel, embed=msg)
    @commands.command(pass_context = True)
    @checks.is_owner()
    async def afksettings(self, ctx):
        """Sets the Server Based Afk"""
        for server in self.bot.servers:
            if not server.id in self.settings:
                self.settings[server.id] = {}
                fileIO("data/afk/afk.json","save",self.settings)
        await self.bot.say("Sucesfully configured the afk command!")
    @commands.command(pass_context=True, name="afk")
    @checks.mod_or_permissions(manage_messages = True)
    async def _away(self, ctx, *, message: str = None):
        """Set yourself as afk or not. Server BASED!"""
        data = fileIO(self.afk_data, 'load')
        server = ctx.message.server
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        author_mention = ctx.message.author.mention
        if author_mention in data[server.id]:
            del data[server.id][author_mention]
            msg = discord.Embed(description="**{}, Welcome Back!**".format(ctx.message.author.name), colour=discord.Colour(value=colour))
        else:
            data[server.id][ctx.message.author.mention] = {}
            if message is not None:
                data[server.id][ctx.message.author.mention]['MESSAGE'] = " ".join(ctx.message.clean_content.split()[1:])
            else:
                data[server.id][ctx.message.author.mention]['MESSAGE'] = False
            msg = discord.Embed(description='**{}, You are now set as afk.**'.format(ctx.message.author.name), colour=discord.Colour(value=colour))
        fileIO(self.afk_data, 'save', data)
        await self.bot.say(embed=msg)

    async def on_server_join(self, server):
        self.settings[server.id] = {}
        fileIO("data/afk/afk.json","save",self.settings)

def check_folder():
    if not os.path.exists('data/afk'):
        print('Creating data/afk folder...')
        os.makedirs('data/afk')

def check_file():
    afk = {}
    f = 'data/afk/afk.json'
    if not fileIO(f, 'check'):
        print('Creating default afk.json...')
        fileIO(f, 'save', afk)
def setup(bot):
    check_folder()
    check_file()
    n = Afk(bot)
    bot.add_listener(n.listener, 'on_message')
    bot.add_cog(n)
