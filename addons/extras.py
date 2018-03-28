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
    async def kotomi(self):
        """About the bot"""
        embed = discord.Embed(title="Kotomi", color=discord.Color.green())
        embed.set_author(name="")
        embed.set_thumbnail(url="https://static.zerochan.net/Ichinose.Kotomi.full.142128.jpg")
        embed.description = "Based off of Homura by Aurora Wright, which is based off of Kurisu by 916253 and ihaveamac"
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
    
    @commands.command(pass_context=True)
    async def setroles(self, ctx, *, text: str):
        """Set pronoun, gender, and orientation roles"""
        if "she/her" in text:
            await self.bot.add_roles(ctx.message.author, self.bot.she_her_role)
        if "they/them" in text:
            await self.bot.add_roles(ctx.message.author, self.bot.they_them_role)
        if "he/him" in text:
            await self.bot.add_roles(ctx.message.author, self.bot.he_him_role)
        if "girl" in text:
            await self.bot.add_roles(ctx.message.author, self.bot.girl_role)
        if "boy" in text:
            await self.bot.add_roles(ctx.message.author, self.bot.boy_role)
        if "non-binary" in text:
            await self.bot.add_roles(ctx.message.author, self.bot.non_binary_role)
        if "straight" in text:
            await self.bot.add_roles(ctx.message.author, self.bot.straight_role)
        if "gay" in text:
            await self.bot.add_roles(ctx.message.author, self.bot.gay_role)
        if "bi/pan" in text:
            await self.bot.add_roles(ctx.message.author, self.bot.bi_pan_role)
        if "ace" in text:
            await self.bot.add_roles(ctx.message.author, self.bot.ace_role)
        if "aro" in text:
            await self.bot.add_roles(ctx.message.author, self.bot.aro_role)
        if "cis" in text:
            await self.bot.add_roles(ctx.message.author, self.bot.cis_role)
        if "trans" in text:
            await self.bot.add_roles(ctx.message.author, self.bot.trans_role)

    @commands.command(pass_context=True)
    async def clearroles(self, ctx):
        """Clears pronoun, gender, and orientation roles"""
        await self.bot.remove_roles(ctx.message.author, *self.bot.extra_roles)

def setup(bot):
    bot.add_cog(Extras(bot))
