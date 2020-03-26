import logging
import os

import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions

bot = commands.Bot(command_prefix='$')
logger = logging.getLogger(__name__)
try:
    log = bot.get_channel(int(os.environ['log']))
except KeyError:
    logger.error("Config vars (log id) inaccessible!") # exception avoided on purpose.
    log_channel = bot.get_channel(616955019727732737)
    logger.info("Alternate id used.")

class moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="unban", aliases=["removeban"], description="A command to unban single user using dicriminator and name eg: $unban example#0000")
    @has_permissions(ban_members=True)
    async def unban(self, ctx, *,member):
        banned_ppl = await ctx.guild.bans()
        member_name,member_discriminator = member.split('#')
        for bans in banned_ppl:
            user = bans.user
            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send("unbanned {user.name}", delete_after = float(5.682))
                await log.send(embed=discord.Embed(title="Unbanned User", description = f"Unbanned {user.name} on request of {ctx.author.name}", colour = 0xffa500))
                return None
        else:
            await ctx.send("Sorry I couldn't find the user, try unbanning them using discord!", delete_after=6.0)


    @commands.command(name="clear", aliases=["purge","clean","delete","del"], description="deletes amount of specified messages, default is 5 eg: \'$clear 10\' or \'$purge 10\' or \'$delete 10\' or \'$del 10\'")
    @has_permissions(manage_messages=True)
    async def clear(self, ctx, amount = 5):
        try:
            await ctx.channel.purge(limit=amount+1)
        except discord.Forbidden:
            log.info(f"Purge request failed due to permissions, channel:{str(ctx.channel)}")
            await ctx.send(embed=discord.Embed(title="Failed",description="I don't have delete messages permission, please check!", colour = 0xffa500))
        except discord.HTTPException:
            log.warning(f"HTTPException caught status code : {discord.HTTPException.status}", exc_info = True)
            await ctx.send(embed=discord.Embed(title="Error", descrition=f"Failed to delete message. status code:{discord.HTTPException.status}", colour=0xff0000))
        else:
            await ctx.send(content=f"Deleted {amount} messages!", delete_after=float(5.682))
            await log.send(embed=discord.Embed(title=f"Deleted {amount} messages", description=f"{amount} messages deleted in {str(ctx.channel)}", colour = 0x39ff14))


    @commands.command(name="ban", aliases = ["banish"], description = "bans a member usage: \"$ban @example#0000 spam\" reason (i.e spam) is optional and default \"Not given\" will be used.")
    @has_permissions(ban_members=True)
    async def ban(self, ctx, member : discord.Member , *,reason="Not given"):
        auth = ctx.author.mention
        vict = member.name
        await member.ban(reason=reason)
        await log.send(embed=discord.Embed(title="Ban!", description=f"{vict} was banned by {auth}").add_field(description=f"reason : {str(reason)}",colour=0x39ff14))

    @commands.command(name="kick", aliases=["begone"], description="kicks a taged member like \"$kick @example#0000\"")
    @has_permissions(kick_members=True)
    async def kick(self, ctx, member : discord.Member , *,reason="Not given"):
        name = member.name
        await member.kick(reason=reason)
        await ctx.send(f"kicked {name}", delete_after=float(5.682))
        await log.send(embed=discord.Embed(title="Kick",description=f"Kicked {member.name}\nreason : {reason}",colour=0x39ff14))

    @commands.command(name="report")
    async def report(self, ctx, user, reason="Not given"):
        try:
            name = user.name
        except Exception:
            pass
        author = ctx.author
        await author.send(f"Reported {user}!\nThe staff look into your matter soon.\nDon't use this feature as spam.")
        await ctx.message.delete()
        channel = discord.Client().get_channel(620203303736836096)
        await channel.send(embed=discord.Embed(title="Report",description=f"{author} reported {user}/{name}\nreason : {reason}",colour=0x39ff14))

    @kick.error
    @ban.error
    @clear.error
    @unban.error
    async def permit_error(self, error, ctx):
        if isinstance(error, MissingPermissions):
            await ctx.send(f"Sorry {ctx.message.author}, you do not have the permissions to do that!")
        else:
            return None

def setup(bot):
    bot.add_cog(moderation(bot))
