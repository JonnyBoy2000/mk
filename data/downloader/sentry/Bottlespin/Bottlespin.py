import discord
from discord.ext import commands
from random import choice


class Bottlespin:
    """Spins a bottle and lands on a random user."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, no_pm=True)
    async def spin(self, ctx):
        """Spin the bottle"""
        author = ctx.message.author
        server = ctx.message.server
        target = choice(list([m.name for m in ctx.message.server.members if str(m.status) == "online" or str(m.status) == "idle"]))

        await self.bot.say("{} spinned the bottle and it landed on {}".format(ctx.message.author.mention, target))


def setup(bot):
    n = Bottlespin(bot)
    bot.add_cog(n)
