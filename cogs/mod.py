import discord
from discord.ext import commands
from .utils.dataIO import dataIO
from .utils import checks
from __main__ import send_cmd_help, settings
from collections import deque, defaultdict
from cogs.utils.chat_formatting import escape_mass_mentions, box, pagify
import os
import time
import copy
import re
import logging
import random
import asyncio
try:
    from tabulate import tabulate
except:
    raise Exception('Run "pip install tabulate" in your CMD/Linux Terminal')
log = logging.getLogger('red.punish')

default_settings = {
    "ban_mention_spam" : False,
    "delete_repeats"   : False,
    "mod-log"          : None
                   }
log = logging.getLogger('red.massmove')

class ModError(Exception):
    pass


class UnauthorizedCaseEdit(ModError):
    pass


class CaseMessageNotFound(ModError):
    pass


class NoModLogChannel(ModError):
    pass


class Mod:
    """Moderation tools."""

    def __init__(self, bot):
        self.bot = bot
        self.whitelist_list = dataIO.load_json("data/mod/whitelist.json")
        self.blacklist_list = dataIO.load_json("data/mod/blacklist.json")
        self.ignore_list = dataIO.load_json("data/mod/ignorelist.json")
        self.filter = dataIO.load_json("data/mod/filter.json")
        self.past_names = dataIO.load_json("data/mod/past_names.json")
        self.past_nicknames = dataIO.load_json("data/mod/past_nicknames.json")
        settings = dataIO.load_json("data/mod/settings.json")
        self.settings = defaultdict(lambda: default_settings.copy(), settings)
        self.cache = defaultdict(lambda: deque(maxlen=3))
        self.cases = dataIO.load_json("data/mod/modlog.json")
        self.last_case = defaultdict(dict)
        self._tmp_banned_cache = []
        perms_cache = dataIO.load_json("data/mod/perms_cache.json")
        self._perms_cache = defaultdict(dict, perms_cache)
        self.location = 'data/antilink/settings.json'
        self.json = dataIO.load_json(self.location)
        self.regex = re.compile(r"<?(https?:\/\/)?(www\.)?(discord\.gg|discordapp\.com\/invite)\b([-a-zA-Z0-9/]*)>?")
        self.regex_discordme = re.compile(r"<?(https?:\/\/)?(www\.)?(discord\.me\/)\b([-a-zA-Z0-9/]*)>?")
        self.location = 'data/punish/settings.json'
        self.json = dataIO.load_json(self.location)
        self.min = ['m', 'min', 'mins', 'minutes', 'minute']
        self.hour = ['h', 'hour', 'hours']
        self.day = ['d', 'day', 'days']
        self.task = bot.loop.create_task(self.check_time())

    def __unload(self):
        self.task.cancel()
        log.debug('Stopped task')

    def _timestamp(self, t, unit):
        if unit in self.min:
            return t * 60 + int(time.time())
        elif unit in self.hour:
            return t * 60 * 60 + int(time.time())
        elif unit in self.day:
            return t * 60 * 60 * 24 + int(time.time())
        else:
            raise Exception('Invalid Unit')

    @commands.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def punish(self, ctx, user: discord.Member, t: int=1, unit='hour'):
        """Places a user in timeout for a period of time.

        Valid unit of times are minutes, hours & days.
        Example usage: r!!punish @Young 3 hours"""
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        server = ctx.message.server
        # --- CREATING ROLE ---
        if 'Punished' not in [r.name for r in server.roles]:
            embed1 = discord.Embed(description='**The Punished role doesn\'t exist! Creating it now!**', colour=discord.Colour(value=colour))
            await self.bot.say(embed=embed1)
            log.debug('Creating Punished role in {}'.format(server.id))
            try:
                perms = discord.Permissions.none()
                await self.bot.create_role(server, name='Punished', permissions=perms)
                embed2 = discord.Embed(description="**Role created! Setting channel permissions!\nPlease ensure that your moderator roles are ABOVE the Punished role!\nPlease wait until the user has been added to the Timeout role!**", colour=discord.Colour(value=colour))
                await self.bot.say(embed=embed2)
                try:
                    r = discord.utils.get(server.roles, name='Punished')
                    perms = discord.PermissionOverwrite()
                    perms.send_messages = False
                    for c in server.channels:
                        if c.type.name == 'text':
                            await self.bot.edit_channel_permissions(c, r, perms)
                            await asyncio.sleep(1.5)
                except discord.Forbidden:
                    embed3 = discord.Embed(description="**A error occured while making channel permissions.\nPlease check your channel permissions for the Punished role!**", colour=discord.Colour(value=colour))
                    await self.bot.say(embed=embed3)
            except discord.Forbidden:
                embed4 = discord.Embed(description="**I cannot create a role. Please assign Manage Roles to me!**", colour=discord.Colour(value=colour))
                await self.bot.say(embed=embed4)
        role = discord.utils.get(server.roles, name='Punished')
        # --- DONE CREATING ROLE! ---
        # --- JSON SERVER LOGIC ---
        if server.id not in self.json:
            log.debug('Adding server({}) in Json'.format(server.id))
            self.json[server.id] = {}
            dataIO.save_json(self.location, self.json)
        # --- DONE JSON SERVER LOGIC! ---
        # --- ASSIGNING TIMESTAMPS AND ROLE ---
        try:
            if user.id == ctx.message.author.id:
                embed5 = discord.Embed(description='**Please don\'t punish yourself :frowning:**', colour=discord.Colour(value=colour))
                await self.bot.say(embed=embed5)
            elif user.id not in self.json[server.id] and role not in user.roles:
                # USER NOT IN PUNISH, NO ROLE
                until = self._timestamp(t, unit)
                self.json[server.id][user.id] = {'until': until, 'givenby': ctx.message.author.id}
                dataIO.save_json(self.location, self.json)
                await self.bot.add_roles(user, role)
                embed6 = discord.Embed(description='**{} is now Punished for {} {} by {}.**'.format(user.display_name, str(t), unit, ctx.message.author.display_name), colour=discord.Colour(value=colour))
                await self.bot.say(embed=embed6)
            elif user.id in self.json[server.id] and role not in user.roles:
                # USER IN PUNISH, NO ROLE
                    await self.bot.add_roles(user, role)
                    embed7 = discord.Embed(description='**Role reapplied on {}.**'.format(user.display_name), colour=discord.Colour(value=colour))
                    await self.bot.say(embed=embed7)
            elif user.id not in self.json[server.id] and role in user.roles:
                # USER NOT IN PUNISH, HAS ROLE
                until = self._timestamp(t, unit)
                self.json[server.id][user.id] = {'until': until, 'givenby': ctx.message.author.id}
                dataIO.save_json(self.location, self.json)
                embed8 = discord.Embed(description='**{} is now Punished for {} {} by {}.**'.format(user.display_name, str(t), unit, ctx.message.author.display_name), colour=discord.Colour(value=colour))
                await self.bot.say(embed=embed8)
            else:
                # USER IN PUNISH, HAS ROLE
                embed9 = discord.Embed(description='**{} is already punished.\nPlease use unpunish to r!!unpunish the user.**'.format(user.display_name), colour=discord.Colour(value=colour))
                await self.bot.say(embed=embed9)
        except:
            embed10 = discord.Embed(description='**Invalid unit**', colour=discord.Colour(value=colour))

    @commands.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def unpunish(self, ctx, user: discord.Member):
        """Unpunishes a punished user"""
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        if user.id in self.json[ctx.message.server.id]:
            r = discord.utils.get(ctx.message.server.roles, name='Punished')
            del self.json[ctx.message.server.id][user.id]
            await self.bot.remove_roles(user, r)
            dataIO.save_json(self.location, self.json)
            embed = discord.Embed(description='**{} is now unpunished.**'.format(user.display_name), colour=discord.Colour(value=colour))
            await self.bot.say(embed=embed)

    @commands.command(pass_context=True, no_pm=True)
    async def muted(self, ctx):
        """Shows the list of punished users"""
        # Populate a list with other lists, they act as tables
        server = ctx.message.server
        table = []
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        if server.id in self.json:
            for user in self.json[server.id]:
                temp = []
                # Get the user display_name
                user_obj = discord.utils.get(server.members, id=user)
                log.debug(user_obj)
                if user_obj is None:
                    temp.append('ID: {}'.format(user))
                else:
                    temp.append(user_obj.display_name)
                    # Get the time in minutes or hours, (hopefully)
                    remaining = self.json[server.id][user]['until'] - int(time.time())
                if remaining < 60:
                    temp.append('<1 Minute')
                elif remaining < 120:
                    temp.append('1 Minute')
                elif remaining < 3600:
                    remaining = remaining / 60
                    temp.append('{} Minutes'.format(int(remaining)))
                elif remaining < 86400:
                    remaining = remaining / 60 / 60
                    temp.append('{} Hours'.format(int(remaining)))
                else:
                    remaining = remaining / 60 / 60 / 24
                    temp.append('{} Days'.format(int(remaining)))
                # Get the givenby
                given_obj = discord.utils.get(server.members, id=self.json[server.id][user]['givenby'])
                if given_obj is None:
                    temp.append('ID: {}'.format(self.json[server.id][user]['givenby']))
                else:
                    temp.append(given_obj.display_name)
                    table.append(temp)
            header = ['Member', 'Time Remaining', 'Given By']
            embed = discord.Embed(description='\n**{}**'.format(tabulate(table, headers=header, tablefmt='simple')), colour=discord.Colour(value=colour))
            await self.bot.say(embed=embed)
        else:
            embed = discord.Embed(description='**No punishments are given out on this server.**', colour=discord.Colour(value=colour))
            await self.bot.say(embed=embed)

    # Look for new channels, and slap the role in there face!
    async def new_channel(self, c):
        if 'Punished' in [r.name for r in c.server.roles]:
            if c.type.name == 'text':
                perms = discord.PermissionOverwrite()
                perms.send_messages = False
                r = discord.utils.get(c.server.roles, name='Punished')
                await self.bot.edit_channel_permissions(c, r, perms)
                log.debug('Punished role created on channel: {}'.format(c.id))

    async def check_time(self):
        while True:
            await asyncio.sleep(30)
            json = copy.deepcopy(self.json)
            log.debug('First Timer')
            for server in json:
                server_obj = discord.utils.get(self.bot.servers, id=server)
                role_obj = discord.utils.get(server_obj.roles, name='Punished')
                log.debug('Server Object = {}'.format(server_obj))
                for user in json[server]:
                    user_obj = discord.utils.get(server_obj.members, id=user)
                    log.debug('User Object = {}'.format(user_obj))
                    if json[server][user]['until'] < int(time.time()):
                        log.debug('Expired user ({})'.format(user))
                        await self.bot.remove_roles(user_obj, role_obj)
                        del self.json[server][user]
                        dataIO.save_json(self.location, self.json)
            log.debug('after loops')

    async def new_member(self, member):
        if member.server.id in self.json:
            if member.id in self.json[member.server.id]:
                r = discord.utils.get(member.server.roles, name='Punished')
                await self.bot.add_roles(member, r)
                log.debug('User ({}) joined while punished.'.format(member.id))

    @commands.group(pass_context=True, hidden=True)
    @checks.is_owner()
    async def blacklist(self, ctx):
        """Bans user from using the bot"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @blacklist.command(name="add")
    async def _blacklist_add(self, user: discord.Member):
        """Adds user to bot's blacklist"""
        if user.id not in self.blacklist_list:
            self.blacklist_list.append(user.id)
            dataIO.save_json("data/mod/blacklist.json", self.blacklist_list)
            await self.bot.say("User has been added to blacklist.")
        else:
            await self.bot.say("User is already blacklisted.")

    @blacklist.command(name="remove")
    async def _blacklist_remove(self, user: discord.Member):
        """Removes user from bot's blacklist"""
        if user.id in self.blacklist_list:
            self.blacklist_list.remove(user.id)
            dataIO.save_json("data/mod/blacklist.json", self.blacklist_list)
            await self.bot.say("User has been removed from blacklist.")
        else:
            await self.bot.say("User is not in blacklist.")

    @blacklist.command(name="clear")
    async def _blacklist_clear(self):
        """Clears the blacklist"""
        self.blacklist_list = []
        dataIO.save_json("data/mod/blacklist.json", self.blacklist_list)
        await self.bot.say("Blacklist is now empty.")

    @commands.command(pass_context=True, hidden=True)
    @checks.is_owner()  # I don't know how permissive this should be yet
    async def whisper(self, ctx, id, *, text):
        author = ctx.message.author

        target = discord.utils.get(self.bot.get_all_members(), id=id)
        if target is None:
            target = self.bot.get_channel(id)
            if target is None:
                target = self.bot.get_server(id)

        prefix = "```diff\n- Message from {}:".format(
            author.name)
        payload = "{}\n\n+ {}```".format(prefix, text)

        try:
            for page in pagify(payload, delims=[" ", "\n"], shorten_by=10):
                await self.bot.send_message(target, page)
        except discord.errors.Forbidden:
            log.debug("Forbidden to send message to {}".format(id))
        except (discord.errors.NotFound, discord.errors.InvalidArgument):
            log.debug("{} not found!".format(id))
        else:
            await self.bot.say("Done.")

    @commands.group(pass_context=True, no_pm=True)
    async def antilinkset(self, ctx):
        """Manages the settings for antilink."""
        serverid = ctx.message.server.id
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
        if serverid not in self.json:
            self.json[serverid] = {'toggle': False, 'message': '', 'dm': False}

    @antilinkset.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(administrator=True)
    async def toggle(self, ctx):
        """Enable/disables antilink in the server"""
        serverid = ctx.message.server.id
        if self.json[serverid]['toggle'] is True:
            self.json[serverid]['toggle'] = False
            await self.bot.say('Antilink is now disabled')
        elif self.json[serverid]['toggle'] is False:
            self.json[serverid]['toggle'] = True
            await self.bot.say('Antilink is now enabled')
        dataIO.save_json(self.location, self.json)

    @antilinkset.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(administrator=True)
    async def message(self, ctx, *, text):
        """Set the message for when the user sends a illegal discord link"""
        serverid = ctx.message.server.id
        self.json[serverid]['message'] = text
        dataIO.save_json(self.location, self.json)
        await self.bot.say('Message is set')
        if self.json[serverid]['dm'] is False:
            await self.bot.say('Remember: Direct Messages on removal is disabled!\nEnable it with ``antilinkset toggledm``')

    @antilinkset.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(administrator=True)
    async def toggledm(self, ctx):
        serverid = ctx.message.server.id
        if self.json[serverid]['dm'] is False:
            self.json[serverid]['dm'] = True
            await self.bot.say('Enabled DMs on removal of invite links')
        elif self.json[serverid]['dm'] is True:
            self.json[serverid]['dm'] = False
            await self.bot.say('Disabled DMs on removal of invite links')
        dataIO.save_json(self.location, self.json)

    async def _new_message(self, message):
        """Finds the message and checks it for regex"""
        user = message.author
        if message.server is None:
            pass
        if message.server.id in self.json:
            if self.json[message.server.id]['toggle'] is True:
                if self.regex.search(message.content) is not None or self.regex_discordme.search(message.content) is not None:
                    roles = [r.name for r in user.roles]
                    bot_admin = settings.get_server_admin(message.server)
                    bot_mod = settings.get_server_mod(message.server)
                    if user.id == settings.owner:
                        pass
                    elif bot_admin in roles:
                        pass
                    elif bot_mod in roles:
                        pass
                    elif user.permissions_in(message.channel).manage_messages is True:
                        pass
                    else:
                        asyncio.sleep(0.5)
                        await self.bot.delete_message(message)
                        if self.json[message.server.id]['dm'] is True:
                            await self.bot.send_message(message.author, self.json[message.server.id]['message'])

    @commands.command(pass_context=True)
    @checks.admin_or_permissions(move_members=True)
    async def massmove(self, ctx, from_channel: discord.Channel, to_channel: discord.Channel):
        """Massmove users to another voice channel.\nExample: r!!massmove Public Music"""
        await self._massmove(ctx, from_channel, to_channel)

    async def _massmove(self, ctx, from_channel, to_channel):
        """Internal function: Massmove users to another voice channel"""
        # check if channels are voice channels. Or moving will be very... interesting...
        type_from = str(from_channel.type)
        type_to = str(to_channel.type)
        if type_from == 'text':
            await self.bot.say('{} is not a valid voice channel'.format(from_channel.name))
            log.debug('SID: {}, from_channel not a voice channel'.format(from_channel.server.id))
        elif type_to == 'text':
            await self.bot.say('{} is not a valid voice channel'.format(to_channel.name))
            log.debug('SID: {}, to_channel not a voice channel'.format(to_channel.server.id))
        else:
            try:
                log.debug('Starting move on SID: {}'.format(from_channel.server.id))
                log.debug('Getting copy of current list to move')
                voice_list = list(from_channel.voice_members)
                for member in voice_list:
                    await self.bot.move_member(member, to_channel)
                    log.debug('Member {} moved to channel {}'.format(member.id, to_channel.id))
                    await asyncio.sleep(0.05)
            except discord.Forbidden:
                await self.bot.say('I have no permission to move members.')
            except discord.HTTPException:
                await self.bot.say('A error occured. Please try again')

    @commands.group(pass_context=True, no_pm=True)
    @checks.serverowner_or_permissions(administrator=True)
    async def modset(self, ctx):
        """Manages server administration settings."""
        if ctx.invoked_subcommand is None:
            server = ctx.message.server
            await send_cmd_help(ctx)
            roles = settings.get_server(server).copy()
            _settings = {**self.settings[server.id], **roles}
            if "delete_delay" not in _settings:
                _settings["delete_delay"] = -1
            msg = ("Admin role: {ADMIN_ROLE}\n"
                   "Mod role: {MOD_ROLE}\n"
                   "Mod-log: {mod-log}\n"
                   "Delete repeats: {delete_repeats}\n"
                   "Ban mention spam: {ban_mention_spam}\n"
                   "Delete delay: {delete_delay}\n"
                   "".format(**_settings))
            await self.bot.say(box(msg))

    @modset.command(name="adminrole", pass_context=True, no_pm=True)
    async def _modset_adminrole(self, ctx, role_name: str):
        """Sets the admin role for this server, case insensitive."""
        server = ctx.message.server
        if server.id not in settings.servers:
            await self.bot.say("Remember to set modrole too.")
        settings.set_server_admin(server, role_name)
        await self.bot.say("Admin role set to '{}'".format(role_name))

    @modset.command(name="modrole", pass_context=True, no_pm=True)
    async def _modset_modrole(self, ctx, role_name: str):
        """Sets the mod role for this server, case insensitive."""
        server = ctx.message.server
        if server.id not in settings.servers:
            await self.bot.say("Remember to set adminrole too.")
        settings.set_server_mod(server, role_name)
        await self.bot.say("Mod role set to '{}'".format(role_name))

    @modset.command(pass_context=True, no_pm=True)
    async def modlog(self, ctx, channel : discord.Channel=None):
        """Sets a channel as mod log

        Leaving the channel parameter empty will deactivate it"""
        server = ctx.message.server
        if channel:
            self.settings[server.id]["mod-log"] = channel.id
            await self.bot.say("Mod events will be sent to {}"
                               "".format(channel.mention))
        else:
            if self.settings[server.id]["mod-log"] is None:
                await send_cmd_help(ctx)
                return
            self.settings[server.id]["mod-log"] = None
            await self.bot.say("Mod log deactivated.")
        dataIO.save_json("data/mod/settings.json", self.settings)

    @modset.command(pass_context=True, no_pm=True)
    async def banmentionspam(self, ctx, max_mentions : int=False):
        """Enables auto ban for messages mentioning X different people

        Accepted values: 5 or superior"""
        server = ctx.message.server
        if max_mentions:
            if max_mentions < 5:
                max_mentions = 5
            self.settings[server.id]["ban_mention_spam"] = max_mentions
            await self.bot.say("Autoban for mention spam enabled. "
                               "Anyone mentioning {} or more different people "
                               "in a single message will be autobanned."
                               "".format(max_mentions))
        else:
            if self.settings[server.id]["ban_mention_spam"] is False:
                await send_cmd_help(ctx)
                return
            self.settings[server.id]["ban_mention_spam"] = False
            await self.bot.say("Autoban for mention spam disabled.")
        dataIO.save_json("data/mod/settings.json", self.settings)

    @modset.command(pass_context=True, no_pm=True)
    async def deleterepeats(self, ctx):
        """Enables auto deletion of repeated messages"""
        server = ctx.message.server
        if not self.settings[server.id]["delete_repeats"]:
            self.settings[server.id]["delete_repeats"] = True
            await self.bot.say("Messages repeated up to 3 times will "
                               "be deleted.")
        else:
            self.settings[server.id]["delete_repeats"] = False
            await self.bot.say("Repeated messages will be ignored.")
        dataIO.save_json("data/mod/settings.json", self.settings)

    @modset.command(pass_context=True, no_pm=True)
    async def resetcases(self, ctx):
        """Resets modlog's cases"""
        server = ctx.message.server
        self.cases[server.id] = {}
        dataIO.save_json("data/mod/modlog.json", self.cases)
        await self.bot.say("Cases have been reset.")

    @modset.command(pass_context=True, no_pm=True)
    async def deletedelay(self, ctx, time: int=None):
        """Sets the delay until the bot removes the command message.
            Must be between -1 and 60.

        A delay of -1 means the bot will not remove the message."""
        server = ctx.message.server
        if time is not None:
            time = min(max(time, -1), 60)  # Enforces the time limits
            self.settings[server.id]["delete_delay"] = time
            if time == -1:
                await self.bot.say("Command deleting disabled.")
            else:
                await self.bot.say("Delete delay set to {}"
                                   " seconds.".format(time))
            dataIO.save_json("data/mod/settings.json", self.settings)
        else:
            try:
                delay = self.settings[server.id]["delete_delay"]
            except KeyError:
                await self.bot.say("Delete delay not yet set up on this"
                                   " server.")
            else:
                if delay != -1:
                    await self.bot.say("Bot will delete command messages after"
                                       " {} seconds. Set this value to -1 to"
                                       " stop deleting messages".format(delay))
                else:
                    await self.bot.say("I will not delete command messages.")

    @commands.command(no_pm=True, pass_context=True)
    @checks.admin_or_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.Member):
        """Kicks user."""
        author = ctx.message.author
        server = author.server
        try:
            await self.bot.kick(user)
            logger.info("{}({}) kicked {}({})".format(
                author.name, author.id, user.name, user.id))
            await self.new_case(server,
                                action="Kick \N{WOMANS BOOTS}",
                                mod=author,
                                user=user)
            await self.bot.say("Done. That felt good.")
        except discord.errors.Forbidden:
            await self.bot.say("I'm not allowed to do that.")
        except Exception as e:
            print(e)

    @commands.command(no_pm=True, pass_context=True)
    @checks.admin_or_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.Member, days: int=0):
        """Bans user and deletes last X days worth of messages.

        Minimum 0 days, maximum 7. Defaults to 0."""
        author = ctx.message.author
        server = author.server
        if days < 0 or days > 7:
            await self.bot.say("Invalid days. Must be between 0 and 7.")
            return
        try:
            self._tmp_banned_cache.append(user)
            await self.bot.ban(user, days)
            logger.info("{}({}) banned {}({}), deleting {} days worth of messages".format(
                author.name, author.id, user.name, user.id, str(days)))
            await self.new_case(server,
                                action="Ban \N{HAMMER}",
                                mod=author,
                                user=user)
            await self.bot.say("Done. It was about time.")
        except discord.errors.Forbidden:
            await self.bot.say("I'm not allowed to do that.")
        except Exception as e:
            print(e)
        finally:
            await asyncio.sleep(1)
            self._tmp_banned_cache.remove(user)

    @commands.command(no_pm=True, pass_context=True)
    @checks.admin_or_permissions(ban_members=True)
    async def softban(self, ctx, user: discord.Member):
        """Kicks the user, deleting 1 day worth of messages."""
        server = ctx.message.server
        channel = ctx.message.channel
        can_ban = channel.permissions_for(server.me).ban_members
        author = ctx.message.author
        try:
            invite = await self.bot.create_invite(server, max_age=3600*24)
            invite = "\nInvite: " + invite
        except:
            invite = ""
        if can_ban:
            try:
                try:  # We don't want blocked DMs preventing us from banning
                    msg = await self.bot.send_message(user, "You have been banned and "
                              "then unbanned as a quick way to delete your messages.\n"
                              "You can now join the server again.{}".format(invite))
                except:
                    pass
                self._tmp_banned_cache.append(user)
                await self.bot.ban(user, 1)
                logger.info("{}({}) softbanned {}({}), deleting 1 day worth "
                    "of messages".format(author.name, author.id, user.name,
                     user.id))
                await self.new_case(server,
                                    action="Softban \N{DASH SYMBOL} \N{HAMMER}",
                                    mod=author,
                                    user=user)
                await self.bot.unban(server, user)
                await self.bot.say("Done. Enough chaos.")
            except discord.errors.Forbidden:
                await self.bot.say("My role is not high enough to softban that user.")
                await self.bot.delete_message(msg)
            except Exception as e:
                print(e)
            finally:
                await asyncio.sleep(1)
                self._tmp_banned_cache.remove(user)
        else:
            await self.bot.say("I'm not allowed to do that.")

    @commands.command(no_pm=True, pass_context=True, hidden=True)
    @checks.admin_or_permissions(manage_nicknames=True)
    async def rename(self, ctx, user : discord.Member, *, nickname=""):
        """Changes user's nickname

        Leaving the nickname empty will remove it."""
        nickname = nickname.strip()
        if nickname == "":
            nickname = None
        try:
            await self.bot.change_nickname(user, nickname)
            await self.bot.say("Done.")
        except discord.Forbidden:
            await self.bot.say("I cannot do that, I lack the "
                "\"Manage Nicknames\" permission.")

    @commands.group(pass_context=True, no_pm=True, invoke_without_command=True)
    @checks.mod_or_permissions(administrator=True)
    async def mute(self, ctx, user : discord.Member):
        """Mutes user in the channel/server

        Defaults to channel"""
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.channel_mute, user=user)

    @mute.command(name="channel", pass_context=True, no_pm=True)
    async def channel_mute(self, ctx, user : discord.Member):
        """Mutes user in the current channel"""
        channel = ctx.message.channel
        overwrites = channel.overwrites_for(user)
        if overwrites.send_messages is False:
            await self.bot.say("That user can't send messages in this "
                               "channel.")
            return
        self._perms_cache[user.id][channel.id] = overwrites.send_messages
        overwrites.send_messages = False
        try:
            await self.bot.edit_channel_permissions(channel, user, overwrites)
        except discord.Forbidden:
            await self.bot.say("Failed to mute user. I need the manage roles "
                               "permission and the user I'm muting must be "
                               "lower than myself in the role hierarchy.")
        else:
            dataIO.save_json("data/mod/perms_cache.json", self._perms_cache)
            await self.bot.say("User has been muted in this channel.")
            await self.new_case(ctx.message.server,
                                    action="Channel Mute :no_mouth:",
                                    mod=ctx.message.author,
                                    user=user)

    @mute.command(name="server", pass_context=True, no_pm=True)
    async def server_mute(self, ctx, user : discord.Member):
        """Mutes user in the server"""
        server = ctx.message.server
        register = {}
        for channel in server.channels:
            if channel.type != discord.ChannelType.text:
                continue
            overwrites = channel.overwrites_for(user)
            if overwrites.send_messages is False:
                continue
            register[channel.id] = overwrites.send_messages
            overwrites.send_messages = False
            try:
                await self.bot.edit_channel_permissions(channel, user,
                                                        overwrites)
            except discord.Forbidden:
                await self.bot.say("Failed to mute user. I need the manage roles "
                                   "permission and the user I'm muting must be "
                                   "lower than myself in the role hierarchy.")
                return
            else:
                await asyncio.sleep(0.1)
        if not register:
            await self.bot.say("That user is already muted in all channels.")
            return
        self._perms_cache[user.id] = register
        dataIO.save_json("data/mod/perms_cache.json", self._perms_cache)
        await self.bot.say("User has been muted in this server.")
        await self.new_case(ctx.message.server,
                                    action="Server Mute :no_mouth:",
                                    mod=ctx.message.author,
                                    user=user)

    @commands.group(pass_context=True, no_pm=True, invoke_without_command=True)
    @checks.mod_or_permissions(administrator=True)
    async def unmute(self, ctx, user : discord.Member):
        """Unmutes user in the channel/server

        Defaults to channel"""
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.channel_unmute, user=user)

    @unmute.command(name="channel", pass_context=True, no_pm=True)
    async def channel_unmute(self, ctx, user : discord.Member):
        """Unmutes user in the current channel"""
        channel = ctx.message.channel
        overwrites = channel.overwrites_for(user)
        if overwrites.send_messages:
            await self.bot.say("That user doesn't seem to be muted "
                               "in this channel.")
            return
        if user.id in self._perms_cache:
            old_value = self._perms_cache[user.id].get(channel.id, None)
        else:
            old_value = None
        overwrites.send_messages = old_value
        is_empty = self.are_overwrites_empty(overwrites)
        try:
            if not is_empty:
                await self.bot.edit_channel_permissions(channel, user,
                                                        overwrites)
            else:
                await self.bot.delete_channel_permissions(channel, user)
        except discord.Forbidden:
            await self.bot.say("Failed to unmute user. I need the manage roles"
                               " permission and the user I'm unmuting must be "
                               "lower than myself in the role hierarchy.")
        else:
            try:
                del self._perms_cache[user.id][channel.id]
            except KeyError:
                pass
            if user.id in self._perms_cache and not self._perms_cache[user.id]:
                del self._perms_cache[user.id] #cleanup
            dataIO.save_json("data/mod/perms_cache.json", self._perms_cache)
            await self.bot.say("User has been unmuted in this channel.")
            await self.new_case(ctx.message.server,
                                    action="Channel Unmute :smiley:",
                                    mod=ctx.message.author,
                                    user=user)

    @unmute.command(name="server", pass_context=True, no_pm=True)
    async def server_unmute(self, ctx, user : discord.Member):
        """Unmutes user in the server"""
        server = ctx.message.server
        if user.id not in self._perms_cache:
            await self.bot.say("That user doesn't seem to have been muted with {0}mute commands. "
                               "Unmute them in the channels you want with `{0}unmute <user>`"
                               "".format(ctx.prefix))
            return
        for channel in server.channels:
            if channel.type != discord.ChannelType.text:
                continue
            if channel.id not in self._perms_cache[user.id]:
                continue
            value = self._perms_cache[user.id].get(channel.id)
            overwrites = channel.overwrites_for(user)
            if overwrites.send_messages is False:
                overwrites.send_messages = value
                is_empty = self.are_overwrites_empty(overwrites)
                try:
                    if not is_empty:
                        await self.bot.edit_channel_permissions(channel, user,
                                                                overwrites)
                    else:
                        await self.bot.delete_channel_permissions(channel, user)
                except discord.Forbidden:
                    await self.bot.say("Failed to unmute user. I need the manage roles"
                                       " permission and the user I'm unmuting must be "
                                       "lower than myself in the role hierarchy.")
                    return
                else:
                    del self._perms_cache[user.id][channel.id]
                    await asyncio.sleep(0.1)
        if user.id in self._perms_cache and not self._perms_cache[user.id]:
            del self._perms_cache[user.id] #cleanup
        dataIO.save_json("data/mod/perms_cache.json", self._perms_cache)
        await self.bot.say("User has been unmuted in this server.")
        await self.new_case(ctx.message.server,
                                    action="Server Unmute :smiley:",
                                    mod=ctx.message.author,
                                    user=user)

    @commands.group(pass_context=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def prune(self, ctx):
        """Deletes messages."""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @prune.command(pass_context=True)
    async def user(self, ctx, user: discord.Member, number: int):
        """Deletes last X messages from specified user.

        Examples:
        cleanup user @\u200bTwentysix 2
        cleanup user Red 6"""

        channel = ctx.message.channel
        author = ctx.message.author
        server = author.server
        is_bot = self.bot.user.bot
        has_permissions = channel.permissions_for(server.me).manage_messages

        def check(m):
            if m.author == user:
                return True
            elif m == ctx.message:
                return True
            else:
                return False

        to_delete = [ctx.message]

        if not has_permissions:
            await self.bot.say("I'm not allowed to delete messages.")
            return

        tries_left = 5
        tmp = ctx.message

        while tries_left and len(to_delete) - 1 < number:
            async for message in self.bot.logs_from(channel, limit=100,
                                                    before=tmp):
                if len(to_delete) - 1 < number and check(message):
                    to_delete.append(message)
                tmp = message
            tries_left -= 1

        logger.info("{}({}) deleted {} messages "
                    " made by {}({}) in channel {}"
                    "".format(author.name, author.id, len(to_delete),
                              user.name, user.id, channel.name))

        if is_bot:
            await self.mass_purge(to_delete)
        else:
            await self.slow_deletion(to_delete)

    @prune.command(pass_context=True)
    async def messages(self, ctx, number: int):
        """Deletes last X messages.

        Example:
        cleanup messages 26"""

        channel = ctx.message.channel
        author = ctx.message.author
        server = author.server
        is_bot = self.bot.user.bot
        has_permissions = channel.permissions_for(server.me).manage_messages

        to_delete = []

        if not has_permissions:
            await self.bot.say("I'm not allowed to delete messages.")
            return

        async for message in self.bot.logs_from(channel, limit=number+1):
            to_delete.append(message)

        logger.info("{}({}) deleted {} messages in channel {}"
                    "".format(author.name, author.id,
                              number, channel.name))

        if is_bot:
            await self.mass_purge(to_delete)
        else:
            await self.slow_deletion(to_delete)

    @commands.command(pass_context=True, hidden=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def reason(self, ctx, case, *, reason : str=""):
        """Lets you specify a reason for mod-log's cases

        Defaults to last case assigned to yourself, if available."""
        author = ctx.message.author
        server = author.server
        try:
            case = int(case)
            if not reason:
                await send_cmd_help(ctx)
                return
        except:
            if reason:
                reason = "{} {}".format(case, reason)
            else:
                reason = case
            case = self.last_case[server.id].get(author.id, None)
            if case is None:
                await send_cmd_help(ctx)
                return
        try:
            await self.update_case(server, case=case, mod=author,
                                   reason=reason)
        except UnauthorizedCaseEdit:
            await self.bot.say("That case is not yours.")
        except KeyError:
            await self.bot.say("That case doesn't exist.")
        except NoModLogChannel:
            await self.bot.say("There's no mod-log channel set.")
        except CaseMessageNotFound:
            await self.bot.say("Couldn't find the case's message.")
        else:
            await self.bot.say("Case #{} updated.".format(case))

    @commands.command()
    async def names(self, user : discord.Member):
        """Show previous names/nicknames of a user"""
        server = user.server
        names = self.past_names[user.id] if user.id in self.past_names else None
        try:
            nicks = self.past_nicknames[server.id][user.id]
            nicks = [escape_mass_mentions(nick) for nick in nicks]
        except:
            nicks = None
        msg = ""
        if names:
            names = [escape_mass_mentions(name) for name in names]
            msg += "**Past 20 names**:\n"
            msg += ", ".join(names)
        if nicks:
            if msg:
                msg += "\n\n"
            msg += "**Past 20 nicknames**:\n"
            msg += ", ".join(nicks)
        if msg:
            await self.bot.say(msg)
        else:
            await self.bot.say("That user doesn't have any recorded name or "
                               "nickname change.")

    @commands.command(pass_context=True, no_pm=True)
    async def serverinfo(self, ctx):
        """Shows server's informations"""
        server = ctx.message.server
        a = len([x.name for x in server.members if x.status == discord.Status.online])
        b = len([x.name for x in server.members if x.status == discord.Status.idle])
        c = len([x.name for x in server.members if x.status == discord.Status.dnd])
        d = len([x.name for x in server.members if x.status == discord.Status.offline])
        total = len([e.name for e in server.members if not e.bot])
        bots = len([e.name for e in server.members if e.bot])
        text_channels = len([x for x in server.channels
                             if x.type == discord.ChannelType.text])
        voice_channels = len(server.channels) - text_channels
        passed = (ctx.message.timestamp - server.created_at).days
        created_at = ("**Created {}. {} days ago.**"
                      "".format(server.created_at.strftime("%d %b %Y %H:%M"),
                                passed))

        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        x = -1
        emojis =  []
        while x < len([r for r in ctx.message.server.emojis]) -1:
            x = x + 1
            emojis.append("<:{}:{}>".format([r.name for r in ctx.message.server.emojis][x], [r.id for r in ctx.message.server.emojis][x]))

        data = discord.Embed(
            description=created_at,
            colour=discord.Colour(value=colour))
        data.add_field(name="Region", value=str(server.region))
        data.add_field(name="Users", value="<:vpOnline:212789758110334977>{}<:vpAway:212789859071426561>{}<:vpDnD:236744731088912384>{}<:vpOffline:212790005943369728>{}\n**Humans:** {}\n**Bots:** {}".format(a, b, c, d, total, bots))
        data.add_field(name="Text Channels", value=text_channels)
        data.add_field(name="Voice Channels", value=voice_channels)
        data.add_field(name="Roles", value=len(server.roles))
        data.add_field(name="Owner", value=str(server.owner))
        data.set_footer(text="Server ID: " + server.id)

        if server.icon_url:
            data.set_author(name=server.name, url=server.icon_url)
            data.set_thumbnail(url=server.icon_url)
        else:
            data.set_author(name=server.name)
        if server.emojis:
            data.add_field(name="Emotes", value=" ".join(emojis))
        else:
            data.add_field(name="Emotes", value="None")

        try:
            await self.bot.say(embed=data)
        except discord.HTTPException:
            await self.bot.say("Your server perm's are fucked. I need `embed links`.")

    @commands.command(pass_context=True, no_pm=True)
    async def userinfo(self, ctx, *, user: discord.Member=None):
        """Shows users's informations"""
        author = ctx.message.author
        server = ctx.message.server

        if not user:
            user = author

        roles = [x.name for x in user.roles if x.name != "@everyone"]

        joined_at = self.fetch_joined_at(user, server)
        since_created = (ctx.message.timestamp - user.created_at).days
        since_joined = (ctx.message.timestamp - joined_at).days
        user_joined = joined_at.strftime("%d %b %Y %H:%M")
        user_created = user.created_at.strftime("%d %b %Y %H:%M")
        member_number = sorted(server.members,
                               key=lambda m: m.joined_at).index(user) + 1

        created_on = "{}\n({} days ago)".format(user_created, since_created)
        joined_on = "{}\n({} days ago)".format(user_joined, since_joined)

        game = "Chilling in {} status".format(user.status)

        if user.game is None:
            pass
        elif user.game.url is None:
            game = "Playing {}".format(user.game)
        else:
            game = "Streaming: [{}]({})".format(user.game, user.game.url)

        if roles:
            roles = sorted(roles, key=[x.name for x in server.role_hierarchy
                                       if x.name != "@everyone"].index)
            roles = ", ".join(roles)
        else:
            roles = "None"

        data = discord.Embed(description=game, colour=user.colour)
        data.add_field(name="Joined Discord on", value=created_on)
        data.add_field(name="Joined this server on", value=joined_on)
        data.add_field(name="Roles", value=roles, inline=False)
        data.set_footer(text="Member #{} | User ID:{}"
                             "".format(member_number, user.id))

    @commands.command(no_pm=True, pass_context=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def addrole(self, ctx, rolename, user: discord.Member=None):
        """Adds a role to a user, defaults to author
        Role name must be in quotes if there are spaces."""
        author = ctx.message.author
        channel = ctx.message.channel
        server = ctx.message.server

        if user is None:
            user = author

        role = self._role_from_string(server, rolename)

        if role is None:
            await self.bot.say('That role cannot be found.')
            return

        if not channel.permissions_for(server.me).manage_roles:
            await self.bot.say('I don\'t have manage_roles.')
            return

        await self.bot.add_roles(user, role)
        await self.bot.say('Added role {} to {}'.format(role.name, user.name))

    @commands.command(no_pm=True, pass_context=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def removerole(self, ctx, rolename, user: discord.Member=None):
        """Removes a role from user, defaults to author
        Role name must be in quotes if there are spaces."""
        server = ctx.message.server
        author = ctx.message.author

        role = self._role_from_string(server, rolename)
        if role is None:
            await self.bot.say("Role not found.")
            return

        if user is None:
            user = author

        if role in user.roles:
            try:
                await self.bot.remove_roles(user, role)
                await self.bot.say("Role successfully removed.")
            except discord.Forbidden:
                await self.bot.say("I don't have permissions to manage roles!")
        else:
            await self.bot.say("User does not have that role.")

    def _role_from_string(self, server, rolename, roles=None):
        if roles is None:
            roles = server.roles
        role = discord.utils.find(lambda r: r.name.lower() == rolename.lower(),
                                  roles)
        try:
            log.debug("Role {} found from rolename {}".format(
                role.name, rolename))
        except:
            log.debug("Role not found for rolename {}".format(rolename))
        return role

    async def mass_purge(self, messages):
        while messages:
            if len(messages) > 1:
                await self.bot.delete_messages(messages[:100])
                messages = messages[100:]
            else:
                await self.bot.delete_message(messages[0])
                messages = []
            await asyncio.sleep(1.5)

    async def slow_deletion(self, messages):
        for message in messages:
            try:
                await self.bot.delete_message(message)
            except:
                pass

    def is_mod_or_superior(self, message):
        user = message.author
        server = message.server
        admin_role = settings.get_server_admin(server)
        mod_role = settings.get_server_mod(server)

        if user.id == settings.owner:
            return True
        elif discord.utils.get(user.roles, name=admin_role):
            return True
        elif discord.utils.get(user.roles, name=mod_role):
            return True
        else:
            return False

    async def new_case(self, server, *, action, mod=None, user, reason=None):
        channel = server.get_channel(self.settings[server.id]["mod-log"])
        if channel is None:
            return

        if server.id in self.cases:
            case_n = len(self.cases[server.id]) + 1
        else:
            case_n = 1

        case = {"case"         : case_n,
                "action"       : action,
                "user"         : user.name,
                "user_id"      : user.id,
                "reason"       : reason,
                "moderator"    : mod.name if mod is not None else None,
                "moderator_id" : mod.id if mod is not None else None}

        if server.id not in self.cases:
            self.cases[server.id] = {}

        tmp = case.copy()
        if case["reason"] is None:
            tmp["reason"] = "Type [p]reason {} <reason> to add it".format(case_n)
        if case["moderator"] is None:
            tmp["moderator"] = "Unknown"
            tmp["moderator_id"] = "Nobody has claimed responsibility yet"

        case_msg = ("**Case #{case}** | {action}\n"
                    "**User:** {user} ({user_id})\n"
                    "**Moderator:** {moderator} ({moderator_id})\n"
                    "**Reason:** {reason}"
                    "".format(**tmp))

        try:
            msg = await self.bot.send_message(channel, case_msg)
        except:
            msg = None

        case["message"] = msg.id if msg is not None else None

        self.cases[server.id][str(case_n)] = case

        if mod:
            self.last_case[server.id][mod.id] = case_n

        dataIO.save_json("data/mod/modlog.json", self.cases)

    async def update_case(self, server, *, case, mod, reason):
        channel = server.get_channel(self.settings[server.id]["mod-log"])
        if channel is None:
            raise NoModLogChannel()

        case = str(case)
        case = self.cases[server.id][case]

        if case["moderator_id"] is not None:
            if case["moderator_id"] != mod.id:
                raise UnauthorizedCaseEdit()

        case["reason"] = reason
        case["moderator"] = mod.name
        case["moderator_id"] = mod.id

        case_msg = ("**Case #{case}** | {action}\n"
                    "**User:** {user} ({user_id})\n"
                    "**Moderator:** {moderator} ({moderator_id})\n"
                    "**Reason:** {reason}"
                    "".format(**case))

        dataIO.save_json("data/mod/modlog.json", self.cases)

        msg = await self.bot.get_message(channel, case["message"])
        if msg:
            await self.bot.edit_message(msg, case_msg)
        else:
            raise CaseMessageNotFound()

    async def check_filter(self, message):
        server = message.server
        if server.id in self.filter.keys():
            for w in self.filter[server.id]:
                if w in message.content.lower():
                    try:
                        await self.bot.delete_message(message)
                        logger.info("Message deleted in server {}."
                                    "Filtered: {}"
                                    "".format(server.id, w))
                        return True
                    except:
                        pass
        return False

    async def check_duplicates(self, message):
        server = message.server
        author = message.author
        if server.id not in self.settings:
            return False
        if self.settings[server.id]["delete_repeats"]:
            self.cache[author].append(message)
            msgs = self.cache[author]
            if len(msgs) == 3 and \
                    msgs[0].content == msgs[1].content == msgs[2].content:
                if any([m.attachments for m in msgs]):
                    return False
                try:
                    await self.bot.delete_message(message)
                    return True
                except:
                    pass
        return False

    async def check_mention_spam(self, message):
        server = message.server
        author = message.author
        if server.id not in self.settings:
            return False
        if self.settings[server.id]["ban_mention_spam"]:
            max_mentions = self.settings[server.id]["ban_mention_spam"]
            mentions = set(message.mentions)
            if len(mentions) >= max_mentions:
                try:
                    self._tmp_banned_cache.append(author)
                    await self.bot.ban(author, 1)
                except:
                    logger.info("Failed to ban member for mention spam in "
                                "server {}".format(server.id))
                else:
                    await self.new_case(server,
                                        action="Ban \N{HAMMER}",
                                        mod=server.me,
                                        user=author,
                                        reason="Mention spam (Autoban)")
                    return True
                finally:
                    await asyncio.sleep(1)
                    self._tmp_banned_cache.remove(author)
        return False

    async def on_command(self, command, ctx):
        """Currently used for:
            * delete delay"""
        server = ctx.message.server
        message = ctx.message
        try:
            delay = self.settings[server.id]["delete_delay"]
        except KeyError:
            # We have no delay set
            return
        except AttributeError:
            # DM
            return

        if delay == -1:
            return

        async def _delete_helper(bot, message):
            try:
                await bot.delete_message(message)
                logger.debug("Deleted command msg {}".format(message.id))
            except discord.errors.Forbidden:
                # Do not have delete permissions
                logger.debug("Wanted to delete mid {} but no"
                             " permissions".format(message.id))

        await asyncio.sleep(delay)
        await _delete_helper(self.bot, message)

    async def on_message(self, message):
        if message.channel.is_private or self.bot.user == message.author \
         or not isinstance(message.author, discord.Member):
            return
        elif self.is_mod_or_superior(message):
            return
        deleted = await self.check_filter(message)
        if not deleted:
            deleted = await self.check_duplicates(message)
        if not deleted:
            deleted = await self.check_mention_spam(message)

    def fetch_joined_at(self, user, server):
        """Just a special case for someone special :^)"""
        if user.id == "96130341705637888" and server.id == "133049272517001216":
            return datetime.datetime(2016, 1, 10, 6, 8, 4, 443000)
        else:
            return user.joined_at

    async def on_member_ban(self, member):
        if member not in self._tmp_banned_cache:
            server = member.server
            await self.new_case(server,
                                user=member,
                                action="Ban \N{HAMMER}")

    async def check_names(self, before, after):
        if before.name != after.name:
            if before.id not in self.past_names:
                self.past_names[before.id] = [after.name]
            else:
                if after.name not in self.past_names[before.id]:
                    names = deque(self.past_names[before.id], maxlen=20)
                    names.append(after.name)
                    self.past_names[before.id] = list(names)
            dataIO.save_json("data/mod/past_names.json", self.past_names)

        if before.nick != after.nick and after.nick is not None:
            server = before.server
            if server.id not in self.past_nicknames:
                self.past_nicknames[server.id] = {}
            if before.id in self.past_nicknames[server.id]:
                nicks = deque(self.past_nicknames[server.id][before.id],
                              maxlen=20)
            else:
                nicks = []
            if after.nick not in nicks:
                nicks.append(after.nick)
                self.past_nicknames[server.id][before.id] = list(nicks)
                dataIO.save_json("data/mod/past_nicknames.json",
                                 self.past_nicknames)

    def are_overwrites_empty(self, overwrites):
        """There is currently no cleaner way to check if a
        PermissionOverwrite object is empty"""
        original = [p for p in iter(overwrites)]
        empty = [p for p in iter(discord.PermissionOverwrite())]
        return original == empty


def check_folders():
    folders = ("data", "data/mod/")
    for folder in folders:
        if not os.path.exists(folder):
            print("Creating " + folder + " folder...")
            os.makedirs(folder)


def check_files():
    ignore_list = {"SERVERS": [], "CHANNELS": []}

    files = {
        "blacklist.json"      : [],
        "whitelist.json"      : [],
        "ignorelist.json"     : ignore_list,
        "filter.json"         : {},
        "past_names.json"     : {},
        "past_nicknames.json" : {},
        "settings.json"       : {},
        "modlog.json"         : {},
        "perms_cache.json"    : {}
    }

    for filename, value in files.items():
        if not os.path.isfile("data/mod/{}".format(filename)):
            print("Creating empty {}".format(filename))
            dataIO.save_json("data/mod/{}".format(filename), value)

def check_folder():
    if not os.path.exists('data/antilink'):
        os.makedirs('data/antilink')


def check_file():
    f = 'data/antilink/settings.json'
    if dataIO.is_valid_json(f) is False:
        dataIO.save_json(f, {})

def check_folder():
    if not os.path.exists('data/punish'):
        log.debug('Creating folder: data/punish')
        os.makedirs('data/punish')


def check_file():
    f = 'data/punish/settings.json'
    if dataIO.is_valid_json(f) is False:
        log.debug('Creating json: settings.json')
        dataIO.save_json(f, {})

def setup(bot):
    global logger
    check_folders()
    check_files()
    logger = logging.getLogger("mod")
    # Prevents the logger from being loaded again in case of module reload
    if logger.level == 0:
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(
            filename='data/mod/mod.log', encoding='utf-8', mode='a')
        handler.setFormatter(
            logging.Formatter('%(asctime)s %(message)s', datefmt="[%d/%m/%Y %H:%M]"))
        logger.addHandler(handler)
    n = Mod(bot)
    bot.add_listener(n.check_names, "on_member_update")
    bot.add_listener(n._new_message, 'on_message')
    bot.add_cog(n)
