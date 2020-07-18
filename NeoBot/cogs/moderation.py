"""Korosensei's Moderation Cog"""

import logging
import sys
from typing import Union, Optional

import discord
from discord.ext import commands

from NeoBot.Utils import NeoContext
logger = logging.getLogger(__name__)

class moderation(commands.Cog):
    """
    A moderation cog in discord.py-rewrite
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.prefixes = bot.prefixes
        self.DeleteTime = bot.DeleteTime

    @commands.command(name="warn")
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx: NeoContext, user: discord.Member, *, reason: str = "No reason"):
        """Warns a discord user and logs it to self.log

        Arguments:
            ctx -- The context object
            usr {str, int} -- User Tag or id.

        Keyword Arguments:
            reason {Optional[str]} -- Provide the reason to warn a user (default: {"No reason"})
        """
        if ctx.is_target():
            return await ctx.send(f"You were warned by Yourself for {reason}")
        if user is not None and ctx.is_above(user):
            await user.send(f"You sere warned in {user.guild.name} for {reason}")
            embed = discord.Embed(title="Member Warned", color=0x3C80E2)
            embed.add_field(
                name="Member", value=f"{user.mention}({user.name}) with id {user.id}", inline=True)
            embed.add_field(name="Mod", value="{}".format(
                ctx.message.author), inline=True)
            embed.add_field(
                name="Reason", value="{}".format(reason), inline=False)
            embed.set_thumbnail(url=user.avatar_url)
            await ctx.send_log(embed=embed)
            return await ctx.send(f"Warned {user.name}!", delete_after=self.DeleteTime)
        elif not ctx.is_above(user):
            return await ctx.send(embed=self.bot.Qembed(ctx, title="Error", content=f"{ctx.target[0].mention} seems to be above you."))
        elif not user:
            return await ctx.send(embed=self.bot.Qembed(ctx, title="Error", content="I could not find that specified user", Colour=3))

    async def unbann(self, ctx: NeoContext, user: discord.Member, reason: str) -> None:
        """Refactored Function to unban an user"""
        await ctx.guild.unban(user)
        embed = discord.Embed(title="Member Unbanned", colour=0xffa500)
        embed.add_field(
            name="Member", value=f"{user.mention}({user.name}) with id {user.id}", inline=True)
        embed.add_field(name="Mod", value="{}".format(
            ctx.message.author), inline=True)
        embed.add_field(
            name="Reason", value="{}".format(reason), inline=False)
        embed.set_thumbnail(url=user.avatar_url)
        await ctx.send_log(embed=embed)
        return None

    @commands.command(name="unban", aliases=["removeban"], description="A command to unban single user using dicriminator and name eg: $unban example#0000")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx: NeoContext, member: Union[int, str], *, reason: str = "None Given"):
        """Unban a banned user

        Arguments:
            ctx {discord.ext.commands.Context()} -- The context object
            member {str, int} -- [description]
            reason {[type]} -- [description]
        """
        # TODO:: [Convert this to a converter]
        if isinstance(member, int):
            user = await self.bot.fetch_user(member)
            bans = await ctx.guild.bans()
            if user in map(lambda x: x.user, bans):
                await self.unbann(ctx, user, reason)
                await ctx.send(f"Unbanned {user}")
            else:
                await ctx.send("Either that user doesn't exist or the user is already unbanned.")
        elif isinstance(member, str):
            banned_ppl = await ctx.guild.bans()
            for bans in banned_ppl:
                user = bans.user
                if str(user) == str(member):
                    await self.unbann(ctx, user, reason)
                    return None
            else:
                await ctx.send(
                    "Sorry I couldn't find the user, try unbanning them using discord or give me the id.")
        else:
            await ctx.send("I couldn't figure out who that is 🙍")

    @commands.command(name="clear",
                      aliases=["purge", "clean", "delete", "del"],
                      description="deletes amount of specified messages, default is 5 eg: \'$clear 10\' or \'$purge 10\' or \'$delete 10\' or \'$del 10\'")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx: NeoContext, amount: int=5):
        """
        Purges the specified amount of messages 
        """
        try:
            await ctx.channel.purge(limit=amount+1)
        except:
            await ctx.send("something ")
        else:
            await ctx.send(content=f"Deleted {amount} messages!", delete_after=self.DeleteTime)
            await ctx.send_log(
                embed=discord.Embed(title=f"Deleted {amount} messages", description=f"{amount} messages deleted in {str(ctx.channel)}", colour=0x39ff14))

    async def log_embed(self, ctx: NeoContext, user: discord.Member, embed: discord.Embed, reason: str) -> None:
        """Refactored code for log message info"""
        embed.add_field(
            name="Member", value=f"{user.name} with id {user.id}", inline=True)
        embed.add_field(name="Mod", value="{}".format(
            ctx.message.author), inline=True)
        embed.add_field(
            name="Reason", value="{}".format(reason), inline=False)
        embed.set_thumbnail(url=user.avatar_url)

    @commands.command(pass_context=True, name="kick", aliases=["begone"], description="kicks a taged member like \"$kick @example#0000\"")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: NeoContext, user: discord.Member, str, int, *, reason: str = "No reason specified") -> None:
        """kicks a user from the guild"""
        if ctx.is_target():
            return await ctx.send(embed=self.bot.Qembed(ctx, content="I cannot kick you, please consider leaving instead"))
        if user is not None and ctx.is_above(user):
            embed = discord.Embed(title="Member Kicked", color=0x3C80E2)
            await self.log_embed(ctx, user, embed, reason)
            await ctx.send_log(embed=embed)
            await ctx.send(f"Kicked {user.name}", delete_after=self.DeleteTime)
            await ctx.author.send(f"You were kicked from {ctx.guild.name} for {reason}")
            await ctx.guild.kick(user, reason=reason)
            await ctx.message.delete()
        elif not ctx.is_above(user):
            return await ctx.send(embed=self.bot.Qembed(ctx, title="Error", content=f"{ctx.target[0].mention} seems to be above you."))
        elif not user:
            return await ctx.send(embed=self.bot.Qembed(ctx, title="Error", content="I could not find that specified user", Colour=3))

    @kick.error
    async def kick_error(self, ctx: NeoContext, error: discord.ext.commands.CommandError) -> None:
        """Error Handlerish for kick command"""
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send("**Sorry, I couldn't find this user**", delete_after=self.DeleteTime)
            await ctx.message.delete()
        elif isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("**You don't have permission to kick users!**", delete_after=self.DeleteTime)
            await ctx.message.delete()
        elif isinstance(error, discord.Forbidden):
            await ctx.send("I don't have sufficient permissions", delete_after=self.DeleteTime)
        else:
            raise error

    @commands.command(name="ban",
                      aliases=["banish"],
                      description="bans a member usage: \"$ban @example#0000 spam\" reason (i.e spam) is optional and default \"Not given\" will be used.")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.Member, *, reason: str = "Not given"):
        """Bans a user"""
        if ctx.is_target():
            return await ctx.send(embed=self.bot.Qembed(ctx, content="I cannot ban you, please consider leaving instead"))
        if not ctx.is_target(user) and ctx.is_above(user):
            embed = discord.Embed(title="Member Banned", color=0x3C80E2)
            await self.log_embed(ctx, user, embed, reason)
            await ctx.send_log(embed=embed)
            await ctx.send(f"Banned {user.name}", delete_after=self.DeleteTime)
            await ctx.author.send(f"You were banned from {ctx.guild.name} for {reason}")
            await ctx.guild.ban(user, reason=reason, delete_message_days=2)
            await ctx.message.delete()
        elif not ctx.is_above(user):
            return await ctx.send(embed=self.bot.Qembed(ctx, title="Error", content=f"{ctx.target[0].mention} seems to be above you."))
        elif not user:
            return await ctx.send(embed=self.bot.Qembed(ctx, title="Error", content="I could not find that specified user", Colour=3))


    @ban.error
    async def ban_error(self, ctx:NeoContext, error: discord.ext.commands.CommandError) -> None:
        """Ban Error handler"""
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send("**Sorry, I couldn't find this user**", delete_after=self.DeleteTime)
            await ctx.message.delete()
        elif isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("**You don't have permission to ban users!**", delete_after=self.DeleteTime)
            await ctx.message.delete()
        elif isinstance(error, discord.Forbidden):
            await ctx.send("I don't have sufficient permissions", delete_after=self.bot.DeleteTime)
        else:
            raise error

    @clear.error
    @unban.error
    async def permit_error(self, ctx: NeoContext, error: discord.ext.commands.CommandError) -> None:
        """Purge, unban error"""
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send(f"Sorry {ctx.message.author}, you do not have the permissions to do that!", delete_after=self.bot.DeleteTime)
        elif isinstance(error, discord.Forbidden):
            await ctx.send("I dont seem to have all required permissions.", delete_after=self.bot.DeleteTime)
        else:
            await ctx.send(embed=discord.Embed(description="**Aww Snap! something went wrong**\nI have informed my devlopers", colour=ctx.author.colour))
            logger.exception("info command failed: %s", error)

    @commands.command(name="userinfo", aliases=["uinfo"], no_pm=True)
    # @commands.has_permissions(ban_members=True)
    async def userinfo(self, ctx: NeoContext, usrr: discord.Member) -> None:
        """Get info on an user"""
        roles = [role.mention for role in user.roles]
        embed = discord.Embed(
            timestamp=ctx.message.created_at, color=user.colour)
        embed.add_field(name="Username", value=str(user), inline=False)
        embed.add_field(name="ID", value=user.id)
        embed.add_field(name="Status", value=user.status, inline=False)
        embed.add_field(name="Highest Role", value=user.top_role.mention)

        embed.add_field(name="Created", value=user.created_at.strftime(
            "%B, %#d %B %Y, %I:%M %p UTC"), inline=False)
        embed.add_field(name="Joined", value=user.joined_at.strftime(
            "%B, %#d %B %Y, %I:%M %p UTC"))
        embed.add_field(name=f"{len(roles)} Roles",
                        value=" ".join(roles), inline=False)
        embed.add_field(name="Bot?", value=user.bot)
        embed.set_author(name=f"User Info - {user}")
        embed.set_thumbnail(url=user.avatar_url)
        embed.set_footer(
            text=f"Requested by {str(ctx.author)}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)
        await ctx.message.delete()

    @commands.command(name="serverinfo", aliases=["si", "guildinfo", "ginfo", "gi"], no_pm=True)
    # @commands.has_permissions(administrator=True)
    async def guildinfo(self, ctx: NeoContext) -> None:
        """Gets the guild info"""
        embed = discord.Embed(title="{}'s info".format(
            ctx.message.guild.name), description="Information on the guild", color=0xcc0000)
        embed.add_field(name="guild Name",
                        value=ctx.message.guild.name, inline=True)
        embed.add_field(name="guild ID",
                        value=ctx.message.guild.id, inline=True)
        embed.add_field(name="Members", value=len(ctx.message.guild.members))
        embed.add_field(
            name="Owner", value=ctx.message.guild.owner, inline=True)
        embed.add_field(name="Role Count", value=len(ctx.message.guild.roles))

        embed.add_field(name="Created", value=ctx.message.guild.created_at.strftime(
            "%B, %#d %B %Y, %I:%M %p UTC"))

        embed.set_thumbnail(url=ctx.message.guild.icon_url)
        embed.set_footer(text=f"Requested by {ctx.message.author}")
        await ctx.send(embed=embed)
        await ctx.message.delete()

    @guildinfo.error
    @userinfo.error
    async def info_error(self, ctx, error):
        """info commands error handler"""
        await ctx.send(embed=discord.Embed(description="**Aww Snap! something went wrong**\nI have informed my devlopers", colour=ctx.author.colour))
        logger.exception("info command failed: %s", error)

def setup(bot):
    """Moderation cog setup"""
    bot.add_cog(moderation(bot))
