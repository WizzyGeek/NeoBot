import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
client = commands.Bot(command_prefix="$")

class moderation(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(name="unban", aliases=["removeban"], description="a command to unban single user using dicriminator and name eg: $unban example#0000")
    @has_permissions(ban_members=True)
    async def unban(self, ctx, *,member):
        banned_ppl = await ctx.guild.bans()
        member_name,member_discriminator = member.split('#')
        for bans in banned_ppl:
            user = bans.user
            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send("unbanned user")

    @commands.command(name="clear", aliases=["purge","clean","delete","del"], description="deletes amount of specified messages, default is 5 eg: \'$clear 10\' or \'$purge 10\' or \'$delete 10\' or \'$del 10\'")
    @has_permissions(delete_messages=True)
    async def clear(self, ctx, amount = 5):
        await ctx.channel.purge(limit=amount+1)

    @commands.command(name="ban")
    @has_permissions(ban_members=True)
    async def ban(self, ctx, member : discord.Member , *,reason=None):
        await member.ban(reason=reason)
        await ctx.send(f"banned {member.mention}")

    @commands.command(name="kick", aliases=["begone"], description="kicks a taged member like \"$kick @example#0000\"")
    @has_permissions(kick_members=True)
    async def kick(self, ctx, member : discord.Member , *,reason=None):
        await member.kick(reason=reason)
        await ctx.send(f"kicked {member.mention}")

    @kick.error
    @ban.error
    @clear.error
    @unban.error
    async def permit_error(self, error, ctx):
        if isinstance(error, MissingPermissions):
            await ctx.send(f"Sorry {ctx.message.author}, you do not have permissions to do that :YEET:")


    """ @client.command()
    async def users(self, ctx):
        users = guild.member_count
        await ctx.send(f"No. of users is {users}")
 """
def setup(client):
    client.add_cog(moderation(client))
