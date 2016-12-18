import discord

class Joinmsg:
    """docstring for join message."""
    def __init__(self, bot):
        self.bot = bot

    async def on_server_join(self, server):
        await self.bot.send_message(server, """**:wave: Hi! My name is Brooklyn, I am here because someone in your server has added me. I was made to fill your discord with music and joy!
My command affix's are `r!!help` and `r!help`.
For music help do `r!help`!
For moderation help and more commands do `r!!help`!
If you need help with anything please don't be afraid to type `r!support` and join that server!
Well, that's it! I hope you enjoy me in your server! :white_check_mark:**""")

    async def on_message(self, message):
        if message.content.startswith('$react'):
            msg = await self.bot.send_message(message.channel, 'React with thumbs up or thumbs down.')

            def check(reaction, user):
                e = str(reaction.emoji)
                return e.startswith(('👍', '👎'))

            res = await self.bot.wait_for_reaction(message=msg, check=check)
            await self.bot.edit_message(msg, '{0.user} reacted with {0.reaction.emoji}!'.format(res))

def setup(bot):
    n = Joinmsg(bot)
    bot.add_cog(n)
