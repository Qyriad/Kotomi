import discord
import json
from discord.ext import commands

class Mod:
    """
    Staff commands.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    async def add_restriction(self, member, rst):
        with open("data/restrictions.json", "r") as f:
            rsts = json.load(f)
        if member.id not in rsts:
            rsts[member.id] = []
        if rst not in rsts[member.id]:
            rsts[member.id].append(rst)
        with open("data/restrictions.json", "w") as f:
            json.dump(rsts, f)

    async def remove_restriction(self, member, rst):
        with open("data/restrictions.json", "r") as f:
            rsts = json.load(f)
        if member.id not in rsts:
            rsts[member.id] = []
        if rst in rsts[member.id]:
            rsts[member.id].remove(rst)
        with open("data/restrictions.json", "w") as f:
            json.dump(rsts, f)

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def quit(self, *gamename):
        """Stops the bot."""
        await self.bot.say("👋 Bye bye!")
        await self.bot.close()

    @commands.has_permissions(ban_members=True)
    @commands.command(pass_context=True, hidden=True)
    async def userinfo(self, ctx, user):
        """Gets user info. SuperOP+."""
        u = ctx.message.mentions[0]
        role = u.top_role.name
        if role == "@everyone":
            role = "@ everyone"
        await self.bot.say("name = {}\nid = {}\ndiscriminator = {}\navatar = {}\nbot = {}\navatar_url = {}\ndefault_avatar = {}\ndefault_avatar_url = <{}>\ncreated_at = {}\ndisplay_name = {}\njoined_at = {}\nstatus = {}\ngame = {}\ncolour = {}\ntop_role = {}\n".format(u.name, u.id, u.discriminator, u.avatar, u.bot, u.avatar_url, u.default_avatar, u.default_avatar_url, u.created_at, u.display_name, u.joined_at, u.status, u.game, u.colour, role))

    @commands.has_permissions(ban_members=True)
    @commands.command(pass_context=True, name="clear")
    async def purge(self, ctx, limit: int):
       """Clears a given number of messages. Staff only."""
       try:
           await self.bot.purge_from(ctx.message.channel, limit=limit)
           msg = "🗑 **Cleared**: {} cleared {} messages in {}".format(ctx.message.author.mention, limit, ctx.message.channel.mention)
           await self.bot.send_message(self.bot.modlogs_channel, msg)
       except discord.errors.Forbidden:
           await self.bot.say("💢 I don't have permission to do this.")

    @commands.has_permissions(kick_members=True)
    @commands.command(pass_context=True, name="reset")
    async def reset(self, ctx, limit: int):
       """Wipes messages in #newcomers and pastes the welcome message again. Staff only."""
       try:
           await self.bot.purge_from(ctx.message.channel, limit=limit)
           msg = "🗑 **Reset**: {} cleared {} messages in {}".format(ctx.message.author.mention, limit, ctx.message.channel.mention)
           await self.bot.send_message(self.bot.modlogs_channel, msg)

           await self.bot.say("Post here to let us know you're here so we can grant you access to the server. Read the rules in {} first!".format(self.bot.welcome_channel.mention))
       except discord.errors.Forbidden:
           await self.bot.say("💢 I don't have permission to do this.")

    @commands.has_permissions(manage_nicknames=True)
    @commands.command(pass_context=True, name="mute")
    async def mute(self, ctx, user, *, reason=""):
        """Mutes a user so they can't speak. Staff only."""
        try:
            try:
                member = ctx.message.mentions[0]
            except IndexError:
                await self.bot.say("Please mention a user.")
                return
            if self.bot.staff_role in member.roles:
                await self.bot.say("You can't mute another staffer with this command!")
                return
            await self.add_restriction(member, "Muted")
            await self.bot.add_roles(member, self.bot.muted_role)
            msg_user = "You were muted!"
            if reason != "":
                msg_user += " The given reason is: " + reason
            try:
                await self.bot.send_message(member, msg_user)
            except discord.errors.Forbidden:
                pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
            await self.bot.say("{} can no longer speak.".format(member.mention))
            msg = "🔇 **Muted**: {} muted {} | {}#{}".format(ctx.message.author.mention, member.mention, self.bot.escape_name(member.name), self.bot.escape_name(member.discriminator))
            if reason != "":
                msg += "\n✏️ __Reason__: " + reason
            else:
                msg += "\nPlease add an explanation below. In the future, it is recommended to use `.mute <user> [reason]` as the reason is automatically sent to the user."
            await self.bot.send_message(self.bot.modlogs_channel, msg)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @commands.has_permissions(manage_nicknames=True)
    @commands.command(pass_context=True, name="unmute")
    async def unmute(self, ctx, user):
        """Unmutes a user so they can speak. Staff only."""
        try:
            try:
                member = ctx.message.mentions[0]
            except IndexError:
                await self.bot.say("Please mention a user.")
                return
            await self.remove_restriction(member, "Muted")
            await self.bot.remove_roles(member, self.bot.muted_role)
            await self.bot.say("{} can now speak again.".format(member.mention))
            msg = "🔈 **Unmuted**: {} unmuted {} | {}#{}".format(ctx.message.author.mention, member.mention, self.bot.escape_name(member.name), self.bot.escape_name(member.discriminator))
            await self.bot.send_message(self.bot.modlogs_channel, msg)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @commands.has_permissions(kick_members=True)
    @commands.command(pass_context=True, name="unverify")
    async def unverify(self, ctx, user, *, reason=""):
        """Probate a user. Staff only."""
        try:
            try:
                member = ctx.message.mentions[0]
            except IndexError:
                await self.bot.say("Please mention a user.")
                return
            if self.bot.staff_role in member.roles:
                await self.bot.say("You can't unverify another staffer with this command!")
                return
            await self.remove_restriction(member, "Verified")
            await self.bot.remove_roles(member, self.bot.verified_role)
            msg_user = "You are no longer verified!"
            if reason != "":
                msg_user += " The given reason is: " + reason
            try:
                await self.bot.send_message(member, msg_user)
            except discord.errors.Forbidden:
                pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
            await self.bot.say("{} is no longer verified.".format(member.mention))
            msg = "🚫 **Un-verified**: {} un-verified {} | {}#{}".format(ctx.message.author.mention, member.mention, self.bot.escape_name(member.name), self.bot.escape_name(member.discriminator))
            if reason != "":
                msg += "\n✏️ __Reason__: " + reason
            else:
                msg += "\nPlease add an explanation below. In the future, it is recommended to use `.unverify <user> [reason]` as the reason is automatically sent to the user."
            await self.bot.send_message(self.bot.modlogs_channel, msg)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @commands.has_permissions(kick_members=True)
    @commands.command(pass_context=True, name="verify")
    async def verify(self, ctx, user):
        """Unprobate a user. Staff only."""
        try:
            member = ctx.message.mentions[0]
            await self.add_restriction(member, "Verified")
            await self.bot.add_roles(member, self.bot.verified_role)
            await self.bot.say("{} is verified.".format(member.mention))
            msg = "⭕️ **Verified**: {} verified {} | {}#{}".format(ctx.message.author.mention, member.mention, self.bot.escape_name(member.name), self.bot.escape_name(member.discriminator))
            await self.bot.send_message(self.bot.modlogs_channel, msg)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @commands.has_permissions(ban_members=True)
    @commands.command(pass_context=True)
    async def playing(self, ctx, *gamename):
        """Sets playing message. Staff only."""
        try:
            await self.bot.change_presence(game=discord.Game(name='{}'.format(" ".join(gamename))))
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @commands.has_permissions(ban_members=True)
    @commands.command(pass_context=True)
    async def status(self, ctx, status):
        """Sets status. Staff only."""
        try:
            if status == "online":
                await self.bot.change_presence(status=discord.Status.online)
            elif status == "offline":
                await self.bot.change_presence(status=discord.Status.offline)
            elif status == "idle":
                await self.bot.change_presence(status=discord.Status.idle)
            elif status == "dnd":
                await self.bot.change_presence(status=discord.Status.dnd)
            elif status == "invisible":
                await self.bot.change_presence(status=discord.Status.invisible)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @commands.has_permissions(ban_members=True)
    @commands.command(pass_context=True, hidden=True)
    async def username(self, ctx, *, username):
        """Sets bot name. Staff only."""
        try:
            await self.bot.edit_profile(username=('{}'.format(username)))
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

def setup(bot):
    bot.add_cog(Mod(bot))
