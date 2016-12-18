from discord.ext import commands
from cogs.utils import checks


class IsLoaded:
    "Checks if a Cog is loaded or not"

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="CogLoaded")
    @checks.is_owner()
    async def cog_loaded(self, cog: str):
        """Checks if a Cog is loaded or not"""

        if cog in self.bot.cogs:
            await self.bot.say("""```Py\nCog "{}" is loaded```""".format(cog))
        else:
            await self.bot.say("""```Py\nCog "{}" is not loaded```""".format(cog))

    @commands.command(name="ClassLoaded", alias=["IsLoaded"])
    @checks.is_owner()
    async def class_loaded(self, cog: str):
        """Checks if a Cogs class is loaded or not (unmaintained)"""

        if self.bot.get_cog(cog) == None:
            await self.bot.say("""```Py\nClass "{}" is not loaded```""".format(cog))
        else:
            await self.bot.say("""```Py\nClass "{}" is loaded```""".format(cog))


def setup(bot):
    n = IsLoaded(bot)
    bot.add_cog(n)
