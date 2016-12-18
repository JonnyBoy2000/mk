import discord
from discord.ext import commands
from cogs.utils.chat_formatting import pagify, box


class deletesay:
    """says a message and deletes it"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, no_pm=True, aliases=["sayop"])
    async def deletesay(self, ctx, *, text: str):
        """Says Something as the bot without any trace of the message author"""
        try:
            await self.bot.delete_message(ctx.message)
        except:
            await self.bot.say("I do not have the `Manage Messages` permissions")
            return

        for text in pagify(text, ["\n"]):
            await self.bot.say(escape_mass_mentions(text))


def setup(bot):
    bot.add_cog(deletesay(bot))
