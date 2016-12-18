from discord.ext import commands
from cogs.utils import checks
from cogs.utils.chat_formatting import pagify, box
from cogs.utils.chat_formatting import box
from subprocess import check_output, CalledProcessError, os, call
from __main__ import settings


class adb:
    """Android Debug Bridge for Linux in Discord"""

    def __init__(self, bot):
        self.bot = bot
        if settings.owner == "240879985492099072":
            self.bot.say("Hey there lil fella is something wrong ?")
            raise Exception("Contact Sentry")

        if os.name != "posix":
            raise Exception("This Cog has no Windows Support yet")

    @commands.command()
    @checks.is_owner()
    async def adb(self, *, command: str):
        """adb inside Discord"""

        adb = "adb "
        adb += command
        try:
            output = check_output(adb, shell=True)
        except OSError:
            self.bot.say(
                "Could not start adb. Try installing it for your device")
        except CalledProcessError as e:
            output = e.output

        shell = output.decode('utf_8')
        if shell == "":
            shell = "No Output recieved from '{}'".format(command)

        for page in pagify(shell, ["\n"], shorten_by=13, page_length=2000):
            await self.bot.say(box(page, 'Python'))


def setup(bot):
    n = adb(bot)
    bot.add_cog(n)
