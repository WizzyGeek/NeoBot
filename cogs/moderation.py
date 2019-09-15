import discord
from discord.ext import commands
client = commands.Bot(command_prefix="$")

class moderation(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def unban(self, ctx, *,member):
        banned_ppl = await ctx.guild.bans()
        member_name,member_discriminator = member.split('#')
        for bans in banned_ppl:
            user = bans.user
            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send

    @commands.command()
    async def clear(self, ctx, amount = 5):
        await ctx.channel.purge(limit=amount+1)

    @commands.command()
    async def ban(self, ctx, member : discord.Member , *,reason=None):
        await member.ban(reason=reason)
        await ctx.send(f"banned {member.mention}")

    @commands.command()
    async def kick(self, ctx, member : discord.Member , *,reason=None):
        await member.kick(reason=reason)

#    @client.command()
#    async def users(ctx):
#        users = guild.member_count
#        await ctx.send(f"No. of users is )

def setup(client):
    client.add_cog(moderation(client))
