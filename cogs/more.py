import discord
import asyncio
import random
import time
import os
import aiohttp
import datetime
import json
import logging
from cogs.utils import checks
from .utils.dataIO import dataIO
from __main__ import send_cmd_help, user_allowed
from discord.ext import commands
from collections import namedtuple
from discord.ext.commands import Paginator as paginate
from cogs.utils.chat_formatting import escape, pagify
from .utils.dataIO import fileIO

OpenRift = namedtuple("Rift", ["source", "destination"])
SETTINGS = "data/weather/settings.json"
log = logging.getLogger('red.massmove')

class More:
    """Some more commands for fun."""

#bot.say("Users Dnd -\n:vpOffline: {0}".format((" \n:vpOffline:".join([e.name for e in server.members if e.permissions_in(message.channel).send_messages and not e.bot and e.status == discord.Status.offline])).replace("`", "")))

    def __init__(self, bot):
        self.bot = bot
        self.open_rifts = {}
        self.settings = fileIO("data/weather/settings.json", "load")

    @commands.group(pass_context=True, no_pm=True)
    async def users(self, ctx):
        """Shows the status's of the users in your server."""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @users.command(pass_context=True)
    @checks.admin_or_permissions(administrator=True)
    async def dnd(self, ctx):
        """Shows users with the status of Dnd. (Lists)"""
        server = ctx.message.server
        e = [e.name for e in server.members if not e.bot and e.status == discord.Status.dnd]
        msg = "**Users with status of Dnd:**\n<:vpDnD:236744731088912384>{0}".format(("\n<:vpDnD:236744731088912384>".join(e)))
        something = pagify(msg, ["\n"])
        for page in something:
            await self.bot.say(page)

    @users.command(pass_context=True)
    @checks.admin_or_permissions(administrator=True)
    async def online(self, ctx):
        """Shows users with the status of Online. (Lists)"""
        server = ctx.message.server
        e = [e.name for e in server.members if not e.bot and e.status == discord.Status.online]
        msg = "**Users with status of Online:**\n<:vpOnline:212789758110334977>{0}".format(("\n<:vpOnline:212789758110334977>".join(e)))
        something = pagify(msg, ["\n"])
        for page in something:
            await self.bot.say(page)

    @users.command(pass_context=True)
    @checks.admin_or_permissions(administrator=True)
    async def idle(self, ctx):
        """Shows users with the status of Idle. (Lists)"""
        server = ctx.message.server
        e = [e.name for e in server.members if not e.bot and e.status == discord.Status.idle]
        msg = "**Users with status of Idle:**\n<:vpAway:212789859071426561>{0}".format(("\n<:vpAway:212789859071426561>".join(e)))
        something = pagify(msg, ["\n"])
        for page in something:
            await self.bot.say(page)

    @users.command(pass_context=True)
    @checks.admin_or_permissions(administrator=True)
    async def offline(self, ctx):
        """Shows users with the status of Offline. (Lists)"""
        server = ctx.message.server
        e = [e.name for e in server.members if not e.bot and e.status == discord.Status.offline]
        msg = "**Users with status of Offline:**\n<:vpOffline:212790005943369728>{0}".format(("\n<:vpOffline:212790005943369728>".join(e)))
        something = pagify(msg, ["\n"])
        for page in something:
            await self.bot.say(page)

    @users.command(pass_context=True)
    async def count(self, ctx):
        """Shows number count."""
        server = ctx.message.server
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        msg = discord.Embed(description="**Fetching users....**",
        colour=discord.Colour(value=colour))
        kkk = await self.bot.say(embed=msg)
        data = discord.Embed(
            description="User Status count for "+server.name+".",
            colour=discord.Colour(value=colour))
        data.add_field(name="**Online<:vpOnline:212789758110334977>**", value=(len([e.name for e in server.members if e.status == discord.Status.online])))
        data.add_field(name="**Idle<:vpAway:212789859071426561>**", value=(len([e.name for e in server.members if e.status == discord.Status.idle])))
        data.add_field(name="**Dnd<:vpDnD:236744731088912384>**", value=(len([e.name for e in server.members if e.status == discord.Status.dnd])))
        data.add_field(name="**Offline<:vpOffline:212790005943369728>**", value=(len([e.name for e in server.members if e.status == discord.Status.offline])))
        data.add_field(name="**Total users:**", value=(len([e.name for e in server.members if not e.bot])))
        data.add_field(name="**Total Bots:**", value=(len([e.name for e in server.members if e.bot])))
        data.set_footer(text="Grand Total: {}".format(len([e.name for e in server.members])))

        if server.icon_url:
            data.set_author(name="", url=server.icon_url)
            data.set_thumbnail(url=server.icon_url)
        else:
            data.set_author(name="")
        await self.bot.edit_message(kkk, embed=data)

    @users.command(pass_context=True, name="all")
    @checks.is_owner()
    async def allservers(self, ctx):
        """Shows all users bot sees."""
        server = ctx.message.server
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        msg = discord.Embed(description="**Fetching users....**",
        colour=discord.Colour(value=colour))
        kkk = await self.bot.say(embed=msg)
        await asyncio.sleep(0.6)
        data = discord.Embed(
            description="User Status count for "+self.bot.user.name+".",
            colour=discord.Colour(value=colour))
        data.add_field(name="**Online<:vpOnline:212789758110334977>**", value=(len([e.name for e in self.bot.get_all_members() if e.status == discord.Status.online])))
        data.add_field(name="**Idle<:vpAway:212789859071426561>**", value=(len([e.name for e in self.bot.get_all_members() if e.status == discord.Status.idle])))
        data.add_field(name="**Dnd<:vpDnD:236744731088912384>**", value=(len([e.name for e in self.bot.get_all_members() if e.status == discord.Status.dnd])))
        data.add_field(name="**Offline<:vpOffline:212790005943369728>**", value=(len([e.name for e in self.bot.get_all_members() if e.status == discord.Status.offline])))
        data.add_field(name="**Total users:**", value=(len([e.name for e in self.bot.get_all_members() if not e.bot])))
        data.add_field(name="**Total Bots:**", value=(len([e.name for e in self.bot.get_all_members() if e.bot])))
        data.set_footer(text="Grand total of {} users in a span of {} servers!".format(len([e.name for e in self.bot.get_all_members()]), len(self.bot.servers)))
        await self.bot.edit_message(kkk, embed=data)

        if server.icon_url:
            data.set_author(name="", url=self.bot.user.avatar_url)
            data.set_thumbnail(url=self.bot.user.avatar_url)
        else:
            data.set_author(name="")
        await self.bot.edit_message(kkk, embed=data)

    @commands.command(pass_context=True, hidden=True)
    async def say2(self, ctx, channel : discord.Channel, *, message):
        try:
            await self.bot.send_message(channel, message)
            await self.bot.say("Done.")
        except discord.errors.Forbidden:
            await self.bot.say("I'm not allowed to send messages to that channel.")

    @commands.group(pass_context=True, no_pm=True)
    async def react(self, ctx):
        """Reaction commands."""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @react.command(pass_context = True, no_pm=True)
    async def emoji(self, ctx, emojis):
        """React with an emoji."""
        async for x in self.bot.logs_from(ctx.message.channel, before=ctx.message.timestamp, limit=1):
                emolist = list(emojis)
                for item in emolist:
                    await self.bot.add_reaction(x, item)

    @react.command(pass_context = True, no_pm=True)
    async def custom(self, ctx, *, reaction):
        """React with your own custom letters."""
        dictionary = { "A" : "\U0001f1e6", "B": "\U0001f1e7", "C": "\U0001f1e8", "D": "\U0001f1e9", "E":  "\U0001f1ea", "F": "\U0001f1eb", "G": "\U0001f1ec", "H" : "\U0001f1ed", "I": "\U0001f1ee", "J": "\U0001f1ef", "K" : "\U0001f1f0", "L": "\U0001f1f1", "M" : "\U0001f1f2", "N" : "\U0001f1f3", "O" : "\U0001f1f4", "P" : "\U0001f1f5", "Q" : "\U0001f1f6",  "R" : "\U0001f1f7", "S" : "\U0001f1f8", "T" : "\U0001f1f9", "U" : "\U0001f1fa", "V" : "\U0001f1fb", "W" : "\U0001f1fc", "X" : "\U0001f1fd", "Y" : "\U0001f1fe", "Z" : "\U0001f1ff"}
        a = reaction
        try:
            listr = [dictionary[char] for char in a]
            dontrun = False
        except KeyError:

            dontrun = True
        lenstr = len(reaction)
        if lenstr > 8:
                await self.bot.say("Length cannot be more than 8 characters")
        elif dontrun == True:
            await self.bot.say("Could not find, Letters only and caps.")
        elif lenstr == 8:
            async for x in self.bot.logs_from(ctx.message.channel, before=ctx.message.timestamp, limit=1):
                try:
                    await self.bot.add_reaction(x, listr[0])
                    await self.bot.add_reaction(x, listr[1])
                    await self.bot.add_reaction(x, listr[2])
                    await self.bot.add_reaction(x, listr[3])
                    await self.bot.add_reaction(x, listr[4])
                    await self.bot.add_reaction(x, listr[5])
                    await self.bot.add_reaction(x, listr[6])
                    await self.bot.add_reaction(x, listr[7])
                except KeyError:
                    await self.bot.say("Could not find, Letters only and caps.")
        elif lenstr == 7:
            async for x in self.bot.logs_from(ctx.message.channel, before=ctx.message.timestamp, limit=1):
                try:
                    await self.bot.add_reaction(x, listr[0])
                    await self.bot.add_reaction(x, listr[1])
                    await self.bot.add_reaction(x, listr[2])
                    await self.bot.add_reaction(x, listr[3])
                    await self.bot.add_reaction(x, listr[4])
                    await self.bot.add_reaction(x, listr[5])
                    await self.bot.add_reaction(x, listr[6])
                except KeyError:
                    await self.bot.say("Could not find, Letters only and caps.")

        elif lenstr == 6:
            async for x in self.bot.logs_from(ctx.message.channel, before=ctx.message.timestamp, limit=1):
                try:
                    await self.bot.add_reaction(x, listr[0])
                    await self.bot.add_reaction(x, listr[1])
                    await self.bot.add_reaction(x, listr[2])
                    await self.bot.add_reaction(x, listr[3])
                    await self.bot.add_reaction(x, listr[4])
                    await self.bot.add_reaction(x, listr[5])
                except KeyError:
                    await self.bot.say("Could not find, Letters only and caps.")
        elif lenstr == 5:
            async for x in self.bot.logs_from(ctx.message.channel, before=ctx.message.timestamp, limit=1):
                try:
                    await self.bot.add_reaction(x, listr[0])
                    await self.bot.add_reaction(x, listr[1])
                    await self.bot.add_reaction(x, listr[2])
                    await self.bot.add_reaction(x, listr[3])
                    await self.bot.add_reaction(x, listr[4])
                except KeyError:
                    await self.bot.say("Could not find, Letters only and caps.")

        elif lenstr == 4:
            async for x in self.bot.logs_from(ctx.message.channel, before=ctx.message.timestamp, limit=1):
                try:
                    await self.bot.add_reaction(x, listr[0])
                    await self.bot.add_reaction(x, listr[1])
                    await self.bot.add_reaction(x, listr[2])
                    await self.bot.add_reaction(x, listr[3])
                except KeyError:
                    await self.bot.say("Could not find, Letters only and caps.")

        elif lenstr == 3:
            async for x in self.bot.logs_from(ctx.message.channel, before=ctx.message.timestamp, limit=1):
                try:
                    await self.bot.add_reaction(x, listr[0])
                    await self.bot.add_reaction(x, listr[1])
                    await self.bot.add_reaction(x, listr[2])
                except KeyError:
                    await self.bot.say("Could not find, Letters only and caps.")

        elif lenstr == 2:
            async for x in self.bot.logs_from(ctx.message.channel, before=ctx.message.timestamp, limit=1):
                try:
                    await self.bot.add_reaction(x, listr[0])
                    await self.bot.add_reaction(x, listr[1])
                except KeyError:
                    await self.bot.say("Could not find, Letters only and caps.")
        elif lenstr == 1:
            async for x in self.bot.logs_from(ctx.message.channel, before=ctx.message.timestamp, limit=1):
                try:
                    await self.bot.add_reaction(x, listr[0])
                except KeyError:
                    await self.bot.say("Could not find, Letters only and caps.")

        else:
            await self.bot.say("Fatal error")

    @react.command(pass_context = True, no_pm=True)
    async def litaf(self, ctx):
        """Lit af."""
        L = "\U0001f1f1"
        I = "\U0001f1ee"
        T = "\U0001f1f9"
        fire = "\U0001f525"
        A = "\U0001f1e6"
        F = "\U0001f1eb"
        ok = "\U0001f44c"

        async for x in self.bot.logs_from(ctx.message.channel, before=ctx.message.timestamp, limit=1):
            await self.bot.add_reaction(x, L)
            await self.bot.add_reaction(x, I)
            await self.bot.add_reaction(x, T)
            await self.bot.add_reaction(x, fire)
            await self.bot.add_reaction(x, A)
            await self.bot.add_reaction(x, F)
            await self.bot.add_reaction(x, ok)

    @react.command(pass_context = True, no_pm=True)
    async def sotru(self, ctx):
        """So true."""
        S = "\U0001f1f8"
        U = "\U0001f1fa"
        O = "\U0001f1f4"
        R = "\U0001f1f7"
        L = "\U0001f1f1"
        I = "\U0001f1ee"
        T = "\U0001f1f9"
        fire = "\U0001f525"
        A = "\U0001f1e6"
        F = "\U0001f1eb"
        ok = "\U0001f44c"
        clap = "\U0001f44f"

        async for x in self.bot.logs_from(ctx.message.channel, before=ctx.message.timestamp, limit=1):
            await self.bot.add_reaction(x, S)
            await self.bot.add_reaction(x, O)
            await self.bot.add_reaction(x, clap)
            await self.bot.add_reaction(x, T)
            await self.bot.add_reaction(x, R)
            await self.bot.add_reaction(x, U)
            await self.bot.add_reaction(x, ok)

    @react.command(pass_context = True, no_pm=True)
    async def idgaf(self, ctx):
        """I don't give a fuck."""
        S = "\U0001f1f8"
        U = "\U0001f1fa"
        D = "\U0001f1e9"
        G = "\U0001f1ec"
        O = "\U0001f1f4"
        R = "\U0001f1f7"
        L = "\U0001f1f1"
        I = "\U0001f1ee"
        T = "\U0001f1f9"
        fire = "\U0001f525"
        A = "\U0001f1e6"
        F = "\U0001f1eb"
        ok = "\U0001f44c"
        clap = "\U0001f44f"
        cool = "\U0001f60e"

        async for x in self.bot.logs_from(ctx.message.channel, before=ctx.message.timestamp, limit=1):
            await self.bot.add_reaction(x, I)
            await self.bot.add_reaction(x, D)
            await self.bot.add_reaction(x, G)
            await self.bot.add_reaction(x, A)
            await self.bot.add_reaction(x, F)
            await self.bot.add_reaction(x, cool)
    @react.command(pass_context = True, no_pm=True)
    async def lmao(self, ctx):
        """Laugh my ass off."""
        L = "\U0001f1f1"
        M = "\U0001f1f2"
        A = "\U0001f1e6"
        O = "\U0001f1f4"
        joy = "\U0001f602"
        cjoy = "\U0001f639"

        async for x in self.bot.logs_from(ctx.message.channel, before=ctx.message.timestamp, limit=1):
            await self.bot.add_reaction(x, L)
            await self.bot.add_reaction(x, M)
            await self.bot.add_reaction(x, A)
            await self.bot.add_reaction(x, O)
            await self.bot.add_reaction(x, joy)
            await self.bot.add_reaction(x, cjoy)

    @react.command(pass_context = True, no_pm=True)
    async def rekt(self, ctx):
        """Rekt hoe."""
        R = "\U0001f1f7"
        E = "\U0001f1ea"
        K = "\U0001f1f0"
        T = "\U0001f1f9"
        FINGERMIDDLE = "\U0001f595"
        FINGERCROSS = "\U0001f91e"

        async for x in self.bot.logs_from(ctx.message.channel, before=ctx.message.timestamp, limit=1):
            await self.bot.add_reaction(x, R)
            await self.bot.add_reaction(x, E)
            await self.bot.add_reaction(x, K)
            await self.bot.add_reaction(x, T)
            await self.bot.add_reaction(x, FINGERMIDDLE)
            await self.bot.add_reaction(x, FINGERCROSS)

    @react.command(pass_context = True, no_pm=True)
    async def noscope(self, ctx):
        """No scoped bitch."""
        N = "\U0001f1f3"
        BOOM = "\U0001f4a5"
        S = "\U0001f1f8"
        C = "\U0001f595"
        O = "\U0001f1f4"
        P = "\U0001f1f5"
        E = "\U0001f1ea"
        GLASSES = "\U0001f576"

        async for x in self.bot.logs_from(ctx.message.channel, before=ctx.message.timestamp, limit=1):
            await self.bot.add_reaction(x, N)
            await self.bot.add_reaction(x, O)
            await self.bot.add_reaction(x, BOOM)
            await self.bot.add_reaction(x, S)
            await self.bot.add_reaction(x, C)
            await self.bot.add_reaction(x, O)
            await self.bot.add_reaction(x, P)
            await self.bot.add_reaction(x, E)
            await self.bot.add_reaction(x, GLASSES)

    @react.command(pass_context = True, no_pm=True)
    async def fucker(self, ctx):
        """You fucker."""
        MIDDLEFINGER = "\U0001f595"
        F = "\U0001f1eb"
        U = "\U0001f1fa"
        C = "\U0001f1e8"
        K = "\U0001f1f0"
        Y = "\U0001f1fe"
        O = "\U0001f1f4"
        E = "\U0001f1ea"
        R = "\U0001f1f7"
        point = "\U0001f446"
        FIST = "\U0001f91c"
        bump = "\U0001f91b"

        async for x in self.bot.logs_from(ctx.message.channel, before=ctx.message.timestamp, limit=1):
            await self.bot.add_reaction(x, MIDDLEFINGER)
            await self.bot.add_reaction(x, F)
            await self.bot.add_reaction(x, U)
            await self.bot.add_reaction(x, C)
            await self.bot.add_reaction(x, K)
            await self.bot.add_reaction(x, E)
            await self.bot.add_reaction(x, R)
            await self.bot.add_reaction(x, bump)

    @react.command(pass_context=True, no_pm=True)
    async def hillary(self, ctx):
        """Hillary."""
        kk = "🇺🇸"
        h = "🇭"
        i = "🇮"
        l = "🇱"
        a = "🇦"
        r = "🇷"
        y = "🇾"
        aa = "🐘"
        async for x in self.bot.logs_from(ctx.message.channel, before=ctx.message.timestamp, limit=1):
            await self.bot.add_reaction(x, kk)
            await self.bot.add_reaction(x, h)
            await self.bot.add_reaction(x, i)
            await self.bot.add_reaction(x, l)
            await self.bot.add_reaction(x, a)
            await self.bot.add_reaction(x, r)
            await self.bot.add_reaction(x, y)
            await self.bot.add_reaction(x, aa)

    @react.command(pass_context=True, no_pm=True)
    async def trump(self, ctx):
        """Trump."""
        mk = "🇺🇸"
        t = "🇹"
        r = "🇷"
        u = "🇺"
        m = "🇲"
        p = "🇵"
        lol = "🐘"
        async for x in self.bot.logs_from(ctx.message.channel, before=ctx.message.timestamp, limit=1):
            await self.bot.add_reaction(x, mk)
            await self.bot.add_reaction(x, t)
            await self.bot.add_reaction(x, r)
            await self.bot.add_reaction(x, u)
            await self.bot.add_reaction(x, m)
            await self.bot.add_reaction(x, p)
            await self.bot.add_reaction(x, lol)

    @react.command(pass_context=True, no_pm=True)
    async def goals(self, ctx):
        """Goals."""
        a = "👉"
        b = "👌"
        c = "💦"
        d = "😣"
        e = "👶"
        f = "👪"
        async for x in self.bot.logs_from(ctx.message.channel, before=ctx.message.timestamp, limit=1):
            await self.bot.add_reaction(x, a)
            await self.bot.add_reaction(x, b)
            await self.bot.add_reaction(x, c)
            await self.bot.add_reaction(x, d)
            await self.bot.add_reaction(x, e)
            await self.bot.add_reaction(x, f)

    @commands.command(pass_context=True, no_pm=True)
    async def say(self, ctx, *, text):
        """Brookyln repeats what you type."""
        channel = ctx.message.channel
        await self.bot.send_message(channel, text)

    @commands.command(no_pm=True, pass_context=False)
    async def weather(self, location, country: str=None):
        """Show your locations tempature."""
        if country is None:
            country = self.settings["defCountry"]
        url = "http://api.wunderground.com/api/" + self.settings['api_key'] + "/conditions/q/" + country + "/" + location +".json"
        async with aiohttp.get(url) as r:
            data = await r.json()
        if "current_observation" in data:
            tempCO = data["current_observation"].get("temperature_string", False)
            tempW = data["current_observation"].get("weather", " ")
            tempC = data["current_observation"].get("temp_c", " ")
            tempF = data["current_observation"].get("temp_f", " ")
            tempH = data["current_observation"].get("relative_humidity", " ")
            if tempCO != False:
                if self.settings["unit"] == "C":
                    await self.bot.say("**Weather **{} **Temp.** {}{} **Hum. **{} ".format(tempW, str(tempC), u"\u2103", tempH))
                elif self.settings["unit"] == "F":
                    await self.bot.say("**Weather **{} **Temp.** {}F **Hum. **{} ".format(tempW, str(tempF), tempH))
            else:
                await self.bot.say("No temperature found")
        else:
            await self.bot.say("`Please use a US zip code or format like: paris fr\nIf the default country is set to your requesting location just '!temp city' will do.\nThe the default country is set to: {} `".format(self.settings["defCountry"]))

    @commands.command(pass_context=True, no_pm=False, hidden=True)
    @checks.admin_or_permissions(manage_server=True)
    async def toggleunit(self, ctx):
        """Switches the default unit: Celcius/Farherheit.
        Admin/owner restricted."""
        user= ctx.message.author
        if self.settings["unit"] == "C":
            self.settings["unit"] = "F"
            allowBot = "Farhenheit"
        elif self.settings["unit"] == "F":
            self.settings["unit"] = "C"
            allowBot = "Celcius"
        await self.bot.say("{} ` The default unit is now: {}.`".format(user.mention, allowBot))
        fileIO(SETTINGS, "save", self.settings)

    @commands.command(pass_context=True, no_pm=False, hidden=True)
    @checks.admin_or_permissions(manage_server=True)
    async def setcountry(self, ctx, country):
        """Sets the default country/zip code.
        Admin/owner restricted."""
        user= ctx.message.author
        if country is None:
            await self.bot.say("{} ` tell me: {}.`".format(user.mention, country))
        else:
            self.settings["defCountry"] = country
            await self.bot.say("{} ` The default country is now: {}.`".format(user.mention, country))
        fileIO(SETTINGS, "save", self.settings)

    @commands.command(pass_context=True, hidden=True)
    @checks.is_owner()
    async def opensource(self, ctx, channel):
        """Makes you able to communicate with other channels.
        This is cross-server. Type only the channel name or the ID."""
        author = ctx.message.author
        author_channel = ctx.message.channel

        def check(m):
            try:
                return channels[int(m.content)]
            except:
                return False

        channels = self.bot.get_all_channels()
        channels = [c for c in channels
                    if c.name.lower() == channel or c.id == channel]
        channels = [c for c in channels if c.type == discord.ChannelType.text]


        if not channels:
            await self.bot.say("No channels found. Remember to type just "
                               "the channel name, no `#`.")
            return

        if len(channels) > 1:
            msg = "Multiple results found.\nChoose a server:\n"
            for i, channel in enumerate(channels):
                msg += "{} - {} ({})\n".format(i, channel.server, channel.id)
            for page in pagify(msg):
                await self.bot.say(page)
            choice = await self.bot.wait_for_message(author=author,
                                                     timeout=30,
                                                     check=check,
                                                     channel=author_channel)
            if choice is None:
                await self.bot.say("You haven't chosen anything.")
                return
            channel = channels[int(choice.content)]
        else:
            channel = channels[0]

        rift = OpenRift(source=author_channel, destination=channel)

        self.open_rifts[author] = rift
        await self.bot.say("A source has been opened! Everything you say "
                           "will be relayed to that channel.\n"
                           "Responses will be relayed here.\nType `exit` to quit.")
        msg = ""
        while msg == "" or msg is not None:
            msg = await self.bot.wait_for_message(author=author,
                                                  channel=author_channel)
            if msg is not None and msg.content.lower() != "exit":
                try:
                    await self.bot.send_message(channel, msg.content)
                except:
                    await self.bot.say("Couldn't send your message.")
            else:
                break
        del self.open_rifts[author]
        await self.bot.say("Source closed.")

    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        for k, v in self.open_rifts.items():
            if v.destination == message.channel:
                msg = "{}: {}".format(message.author, message.content)
                msg = escape(msg, mass_mentions=True)
                await self.bot.send_message(v.source, msg)

    @commands.command(pass_context=True, name="suicide")
    async def commitsuicide(self, ctx):
        """Commit suicide."""
        await self.bot.type()
        await asyncio.sleep(1.5)
        em = discord.Embed(description=" **```diff\n- {} has committed suicide.```**".format(ctx.message.author.name))
        await self.bot.say(embed=em)

    @commands.command(pass_context=True, hidden=True)
    async def ping(self,ctx):
        """Pong."""
        channel = ctx.message.channel
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        t1 = time.perf_counter()
        await self.bot.send_typing(channel)
        t2 = time.perf_counter()
        em = discord.Embed(description="**Pong: {}ms! :ping_pong:**".format(round((t2-t1)*100)), colour=discord.Colour(value=colour))

        await self.bot.say(embed=em)

    @commands.command(pass_context=True, hidden=True)
    @checks.is_owner()
    async def sneek(self, ctx, idnum=None):
        """Lists servers and generates invites for them"""
        owner = ctx.message.author
        if idnum:
            server = discord.utils.get(self.bot.servers, id=idnum)
            if server:
                await self._confirm_invite(server, owner, ctx)
            else:
                await self.bot.say("I'm not in that server")
        else:
            servers = list(self.bot.servers)
            server_list = {}
            msg = ""
            for i in range(0, len(servers)):
                server_list[str(i)] = servers[i]
                msg += "{}: {}\n".format(str(i), servers[i].name)
            msg += "\nTo post an invite for a server just type its number."
            try:
                await self.bot.say(msg)
            except discord.errors.HTTPException:
                await self.bot.say("List too long...sorry")
                return
            msg = await self.bot.wait_for_message(author=owner, timeout=15)
            if msg is not None:
                msg = msg.content.strip()
                if msg in server_list.keys():
                    await self._confirm_invite(server_list[msg], owner, ctx)

    async def _confirm_invite(self, server, owner, ctx):
        answers = ("yes", "y")
        invite = await self.bot.create_invite(server)
        if ctx.message.channel.is_private:
            await self.bot.say(invite)
        else:
            await self.bot.say("Are you sure you want to post an invite to {} "
                               "here? (yes/no)".format(server.name))
            msg = await self.bot.wait_for_message(author=owner, timeout=15)
            if msg is None:
                await self.bot.say("I guess not.")
            elif msg.content.lower().strip() in answers:
                await self.bot.say(invite)
            else:
                await self.bot.say("Alright then.")

    @commands.command(pass_context=True)
    async def info(self, message):
        """Shows info about Brooklyn"""
        server_url = "https://discord.gg/PdXQMPH"
        dpy_repo = "https://github.com/Rapptz/discord.py"
        python_url = "https://www.python.org/"
        since = datetime.datetime(2016, 1, 2, 0, 0)
        dpy_version = "[{}]({})".format(discord.__version__, dpy_repo)
        py_version = "[{}.{}.{}]({})".format(*os.sys.version_info[:3],
                                             python_url)

        owner = "Yσυηg Sιηαтяα™"

        about = (
            "This is a music bot with many features!"
            " I hope you enjoy having Brooklyn in your server!\n\n"
            "Brooklyn is a user friendly bot and "
            "is very easy to use! [Join us today]({}) "
            "for any support you need!\n\n"
            "".format(server_url))

        servers = ("**Brooklyn is currently on {} servers!**".format(len(self.bot.servers)))

        embed = discord.Embed(colour=discord.Colour.red())
        embed.add_field(name="Owner", value=str(owner))
        embed.add_field(name="Python", value=py_version)
        embed.add_field(name="discord.py version", value=dpy_version)
        embed.add_field(name="About Brooklyn", value=about, inline=False)
        embed.add_field(name="Server Count", value=servers, inline=False)

        try:
            await self.bot.say(embed=embed)
        except discord.HTTPException:
            await self.bot.say("I need the `Embed links` permission "
                               "to send this")

    @commands.command(pass_context=True)
    async def invite(self, ctx):
        """Send's you my invite link to add me to your server."""
        await self.bot.say(ctx.message.author.mention+",  Bot accounts can't use invite links!  Click here to add me to a server:\nhttps://discordapp.com/oauth2/authorize?client_id=226132382846156800&scope=bot&permissions=-1")

    @commands.command(pass_context=True)
    async def support(self, ctx):
        """Send's you my support server."""
        await self.bot.type()
        await asyncio.sleep(0.9)
        await self.bot.say("**{}, I have sent you my support server in DM's!**".format(ctx.message.author.mention))
        await self.bot.whisper("**Hi! I noticed you triggered my support command! My owner will be glad to help you! Just join the server and mention <@!146040787891781632> with your concers or questions!\nhttps://discord.gg/fmuvSX9**")

    @commands.command(pass_context=True)
    async def servers(self, ctx):
        """Shows how many server Brooklyn is in."""
        await self.bot.say(ctx.message.author.mention+"**, Brooklyn Radio is currently on {} servers! :confetti_ball:**".format(len(self.bot.servers)))

def check_folders():
    if not os.path.exists("data/weather"):
        print("Creating data/weather folder...")
        os.makedirs("data/weather")

def check_files():
    settings = {"api_key": "Get your API key from: www.wunderground.com/weather/api/", "unit": "C", "defCountry": "uk" }

    if not fileIO(SETTINGS, "check"):
        print("Creating settings.json")
        print("You must obtain an API key as noted in the newly created 'settings.json' file")
        fileIO(SETTINGS, "save", settings)

def setup(bot):
    check_folders()
    check_files()
    n = More(bot)
    bot.add_cog(n)
