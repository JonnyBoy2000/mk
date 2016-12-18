import discord
from discord.ext import commands
from random import choice


class Nep:
    "Nep Nep"

    def __init__(self, bot):
        self.bot = bot

    @commands.command(no_pm=True, aliases=["nep"])
    async def Nep(self):
        """Displays a random Nep."""

        nep = ["http://i.imgur.com/13hoMVJ.jpg",
               "http://i.imgur.com / kIzXdwN.jpg",
               "http://i.imgur.com/DICh64t.jpg",
               "http://i.imgur.com/nMp3NMp.png",
               "http://i.imgur.com/MMf1YfR.png",
               "http://i.imgur.com/CGABJEs.jpg",
               "http://i.imgur.com/GRz1oCo.jpg"]

        nep = choice(nep)

        nepsay = ["Nep!!11", "Neeeeeeepppppp", "Neeeeeeeeeeeeeeeeeeeeeeepppppppppp",
                  "Nep Nep :P", "*intense nepping*", "I ran out of Nep so here is some more"]
        nepsay = choice(nepsay)

        colour = ''.join([choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)

        data = discord.Embed(
            description="", colour=discord.Colour(value=colour))
        data.add_field(name=nepsay, value=u"\u2063")
        data.set_image(url=nep)

        try:
            await self.bot.say(embed=data)
        except:
            await self.bot.say("I need the `Embed links` permission "
                               "to send this")


def setup(bot):
    n = Nep(bot)
    bot.add_cog(n)
