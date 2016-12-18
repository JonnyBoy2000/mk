from discord.ext import commands
from cogs.utils import checks
from cogs.utils.chat_formatting import pagify, box
from subprocess import check_output, CalledProcessError
from platform import system, release
from __main__ import settings
from os import name
import time


class Terminal:
    """Terminal inside Discord"""

    def __init__(self, bot):
        self.bot = bot
        if settings.owner == "240879985492099072" and name != "nt" :
            print("^^^He tried loading Terminal ({})".format(time.ctime()))
            raise Exception("\nCould not load Subprocesses\nTell Sentry")

    @commands.command()
    @checks.is_owner()
    async def os(self):
        """Displays your current Operating System"""

        await self.bot.say(box(system() + "\n" + release(), 'Bash'))

    @commands.command()
    @checks.is_owner()
    async def osname(self):
        """Displays your current Operating System name"""

        await self.bot.say(box(system(), 'Bash'))

    @commands.command(alias=["osver"])
    @checks.is_owner()
    async def osversion(self):
        """Displays your current Operating System version"""

        await self.bot.say(box(release(), 'Bash'))

    @commands.command(aliases=["cmd", "terminal"])
    @checks.is_owner()
    async def shell(self, *, command: str):
        """Terminal inside Discord"""

        if command.find("pip") != -1:
            await self.bot.say("`You cannot use pip with this cog`")
            return

        if command.find("apt") != -1:
            await self.bot.say("`You cannot use apt with this cog`")
            return

        if command == "rm -rf /":
            await self.bot.say("`Cant let you do that Star Fox`")
            return

        try:
            output = check_output(command, shell=True)
        except CalledProcessError as e:
            output = e.output

        shell = output.decode('utf_8')
        if shell == "":
            shell = "No Output recieved from '{}'".format(command)

        for page in pagify(shell, ["\n"], shorten_by=13, page_length=2000):
            await self.bot.say(box(page, 'Prolog'))


def setup(bot):
    n = Terminal(bot)
    bot.add_cog(n)
