import discord
from discord.ext import commands

class Extras:
    """
    Extra things.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    @commands.command()
    async def homura(self):
        """About the bot"""
        embed = discord.Embed(title="Homura", color=discord.Color.green())
        embed.set_author(name="")
        embed.set_thumbnail(url="https://i.imgur.com/KbAseVG.png")
        embed.description = "Based off of Kurisu by 916253 and ihaveamac"
        await self.bot.say("", embed=embed)

    @commands.command()
    async def membercount(self):
        """Prints the member count of the server."""
        await self.bot.say("{} has {:,} members!".format(self.bot.server.name, self.bot.server.member_count))

    @commands.has_permissions(ban_members=True)
    @commands.command(hidden=True)
    async def embedtext(self, *, text):
        """Embed content."""
        await self.bot.say(embed=discord.Embed(description=text))

def setup(bot):
    bot.add_cog(Extras(bot))
