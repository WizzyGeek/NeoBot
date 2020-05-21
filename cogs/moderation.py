import logging
import os

import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions


logger = logging.getLogger(__name__)

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
                #await log.send(embed=discord.Embed(title="Unbanned User", description = f"Unbanned {user.name} on request of {ctx.author.name}", colour = 0xffa500))
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
            log.warning(f"HTTPException caught, status code : {discord.HTTPException.status}", exc_info = True)
            await ctx.send(embed=discord.Embed(title="Error", descrition=f"Failed to delete message. status code:{discord.HTTPException.status}", colour=0xff0000))
        else:
            await ctx.send(content=f"Deleted {amount} messages!", delete_after=float(5.682))
            #await log.send(embed=discord.Embed(title=f"Deleted {amount} messages", description=f"{amount} messages deleted in {str(ctx.channel)}", colour = 0x39ff14))
            

    @commands.command(pass_context=True, name="kick", aliases=["begone"], description="kicks a taged member like \"$kick @example#0000\"")
    @commands.has_permissions(kick_members=True) 
    async def kick(self, ctx, user: discord.Member, *, reason: str = "No reason specified"):
        guild = ctx.message.guild
        log_channel = discord.utils.get(ctx.message.guild.channels, id = 709339678863786084)
        userID = (user.id)
        embed = discord.Embed(title="Member Kicked", color = 0x3C80E2)
        embed.add_field(name="Member", value="{} ".format(user) + "(<@{}>)".format(userID), inline=True)
        embed.add_field(name="Mod", value="{}".format(ctx.message.author), inline=True)
        embed.add_field(name="Reason", value="{}".format(reason), inline=False)
        embed.set_thumbnail(url=user.avatar_url)
        embed.timestamp = datetime.utcnow()
        
        await self.bot.send(log_channel, embed=embed)
        await ctx.send(f"Kicked {user.name}", delete_after = 7.0)
        await self.bot.kick(user)
        await self.bot.delete_message(ctx.message)
        
    @kick.error
    async def kick_error(self, error, ctx):
        if isinstance(error, commands.MissingRequiredArgument):
            userID = (ctx.message.author.id)
            botMessage = await self.bot.send(ctx.message.channel,"<@%s>: **Sorry, I couldn't find this user**" % (userID), delete_after=5.0)
            await self.bot.delete_message(ctx.message)              
        elif isinstance(error, commands.MissingPermissions): # Message to the user if they don't have perms
            userID = (ctx.message.author.id)
            await self.bot.send(ctx.message.author,"<@%s>: **You don't have permission to kick users!**" % (userID), delete_after=5.0)
            await self.bot.delete_message(ctx.message)
        else:
            raise error
        
    @commands.command(name="ban", aliases = ["banish"], description = "bans a member usage: \"$ban @example#0000 spam\" reason (i.e spam) is optional and default \"Not given\" will be used.")
    @commands.has_permissions(ban_members=True) 
    async def ban(self, ctx, user: discord.Member, *, reason: str = "Not given"):
        guild = ctx.message.guild
        log_channel = discord.utils.get(ctx.message.guild.channels, id = 709339678863786084)
        userID = (user.id)
        embed = discord.Embed(title="Member Banned", color = 0x3C80E2)
        embed.add_field(name="Member", value="{} ".format(user) + "(<@{}>)".format(userID), inline=True)
        embed.add_field(name="Mod", value="{}".format(ctx.message.author), inline=True)
        embed.add_field(name="Reason", value="{}".format(reason), inline=False)
        embed.set_thumbnail(url=user.avatar_url)
        embed.timestamp = datetime.utcnow()
        
        await self.bot.send(log_channel, embed=embed)
        await ctx.send(f"Banned {user.name}", delete_after = 7.0)
        await self.bot.kick(user)
        await self.bot.delete_message(ctx.message)
        
    @ban.error
    async def ban_error(self, error, ctx):
        if isinstance(error, commands.MissingRequiredArgument):
            userID = (ctx.message.author.id)
            botMessage = await self.bot.send(ctx.message.channel,"<@%s>: **Sorry, I couldn't find this user**" % (userID), delete_after=5.0)
            await self.bot.delete_message(ctx.message)              
        elif isinstance(error, commands.MissingPermissions):
            userID = (ctx.message.author.id)
            await self.bot.send(ctx.message.author,"<@%s>: **I don't have permission to ban users!**" % (userID), delete_after=5.0)
            await self.bot.delete_message(ctx.message)
        else:
            raise error
            
            
    @clear.error
    @unban.error
    async def permit_error(self, error, ctx):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(f"Sorry {ctx.message.author}, you do not have the permissions to do that!")
        else:
            return None
    
    @commands.command(pass_context=True)
    @commands.has_permissions(ban_members=True)
    async def info(self, ctx, user: discord.Member):
        embed = discord.Embed(title="{}'s Info".format(user.name), color=0x00cda1)
        embed.add_field(name="Username", value=user, inline=True)
        embed.add_field(name="ID", value=user.id, inline=True)
        embed.add_field(name="Status", value=user.status, inline=True)
        embed.add_field(name="Highest Role", value=user.top_role)

        userMade = user.created_at
        userMade2 = userMade.strftime("%B %d, %Y %I:%M %p")
        embed.add_field(name="Created", value="{}".format(userMade2))

        userJoin = user.joined_at
        userJoin2 = userJoin.strftime("%B %d, %Y %I:%M %p")
        embed.add_field(name="Joined", value="{}".format(userJoin2))

        embed.set_thumbnail(url=user.avatar_url)
        embed.set_footer(text="Requested by {}".format(ctx.message.author))
        embed.timestamp = datetime.utcnow()
        await self.bot.say(embed=embed)
        await self.bot.delete_message(ctx.message)
        
    
    @info.error
    async def info_error(self, error, ctx):
        if isinstance(error, discord.ext.commands.BadArgument):
            userID = (ctx.message.author.id)
            botMessage = await self.bot.send(ctx.message.channel,"<@%s>: **Sorry, I couldn't find this user**" % (userID))
            await self.bot.delete_message(ctx.message)        
            await asyncio.sleep(5)
            try:
                await self.bot.delete_message(botMessage)
            except:
                pass
        
        elif isinstance(error, discord.ext.commands.CheckFailure):
            userID = (ctx.message.author.id)
            await self.bot.send(ctx.message.author,"<@%s>: **You don't have permission to perform this action**" % (userID))
            await self.bot.delete_message(ctx.message)
            
    @commands.command(pass_context=True)
    @commands.has_permissions(administrator=True)
    async def guildinfo(self, ctx):
        embed = discord.Embed(title="{}'s info".format(ctx.message.guild.name), description="Information on the guild", color=0xcc0000)
        embed.add_field(name="guild Name", value=ctx.message.guild.name, inline=True)
        embed.add_field(name="guild ID", value=ctx.message.guild.id, inline=True)
        embed.add_field(name="Members", value=len(ctx.message.guild.members))
        embed.add_field(name="Owner", value=ctx.message.guild.owner, inline=True)
        embed.add_field(name="Role Count", value=len(ctx.message.guild.roles))

        servMade = ctx.message.guild.created_at
        servMade2 = servMade.strftime("%B %d, %Y %I:%M %p")
        embed.add_field(name="Created", value="{}".format(servMade2))

        embed.set_thumbnail(url=ctx.message.guild.icon_url)
        embed.set_footer(text="Requested by {}".format(ctx.message.author))
        embed.timestamp = datetime.utcnow()
        await self.bot.say(embed=embed)
        print("guild Info requested")
        await self.bot.delete_message(ctx.message)
        
    @guildinfo.error
    async def guildinfo_error(self, error, ctx):
        if isinstance(error, discord.ext.commands.CheckFailure):
            userID = (ctx.message.author.id)
            await self.bot.send(ctx.message.author,"<@%s>: **You don't have permission to perform this action**" % (userID))
            await self.bot.delete_message(ctx.message)

def setup(bot):
    bot.add_cog(moderation(bot))
