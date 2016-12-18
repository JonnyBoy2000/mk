import discord
from discord.ext import commands
from __main__ import send_cmd_help
from cogs.utils.chat_formatting import pagify

class UserStatus:
    """Shows user status's in servers."""

    def __init__(self, bot):
        self.bot = bot
        
    @commands.group(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(administrator=True)
    async def users(self, ctx):
        """Shows the status's of the users in your server."""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @users.command(pass_context=True)
    async def dnd(self, ctx):
        """Shows users with the status of Dnd."""
        server = ctx.message.server
        e = [e.name for e in server.members if not e.bot and e.status == discord.Status.dnd]
        msg = "**Users with status of Dnd:**\n<:vpDnD:236744731088912384>{0}".format(("\n<:vpDnD:236744731088912384>".join(e)))
        something = pagify(msg, ["\n"])
        for page in something:
            await self.bot.say(page)

    @users.command(pass_context=True)
    async def online(self, ctx):
        """Shows users with the status of Online."""
        server = ctx.message.server
        e = [e.name for e in server.members if not e.bot and e.status == discord.Status.online]
        msg = "**Users with status of Online:**\n<:vpOnline:212789758110334977>{0}".format(("\n<:vpOnline:212789758110334977>".join(e)))
        something = pagify(msg, ["\n"])
        for page in something:
            await self.bot.say(page)

    @users.command(pass_context=True)
    async def idle(self, ctx):
        """Shows users with the status of Idle."""
        server = ctx.message.server
        e = [e.name for e in server.members if not e.bot and e.status == discord.Status.idle]
        msg = "**Users with status of Idle:**\n<:vpAway:212789859071426561>{0}".format(("\n<:vpAway:212789859071426561>".join(e)))
        something = pagify(msg, ["\n"])
        for page in something:
            await self.bot.say(page)

    @users.command(pass_context=True)
    async def offline(self, ctx):
        """Shows users with the status of offline."""
        server = ctx.message.server
        e = [e.name for e in server.members if not e.bot and e.status == discord.Status.offline]
        msg = "**Users with status of Offline:**\n<:vpOffline:212790005943369728>{0}".format(("\n<:vpOffline:212790005943369728>".join(e)))
        something = pagify(msg, ["\n"])
        for page in something:
            await self.bot.say(page)
        
def setup(bot):
    n = UserStatus(bot)
    bot.add_cog(n)
