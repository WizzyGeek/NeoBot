import discord
from discord.ext import commands

from utils.utility import LevelsQuery, ranking

client = commands.Bot(command_prefix="$")

class level(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.command(name="level", aliases=["levelquery"], description="returns your level or another members level requires ping.")
    async def UserLevelQuery(self, ctx, user = None):
        if user == None:
            user = ctx.author.id
        else:
            id = user.id
            user = id
        QueryResult = await LevelsQuery(user)
        try:
            XP = QueryResult[0]
            lvl = QueryResult[1]
            rank = QueryResult[2]
        except TypeError:
            await ctx.send(f"{client.get_user(user).mention} is unranked!")
        embed = discord.Embed(title=f"{client.get_user(user).mention}'s level info", description=f"**Rank**: {rank}\n**lvl**: {lvl}\n**XP**: {XP}", colour=discord.Color.dark_blue())
        await ctx.send(embed=embed)
        return None
        
    @commands.command(name="leaderboard", aliases=["lb"], description="gives the leaderboard, can be used as $lb")
    async def leaderboard(self, ctx):
        await ctx.send("this might take a second...")
        users = [f'{str(i[0])}.{str(i[1][0])}' for i in list(enumerate(await ranking(10), start=1))]
        embed = discord.Embed(title="Leaderboard", colour=discord.Color.dark_blue())
        #embed.add_field(name="rank", value=str("\n".join(series)), inline=True)
        embed.add_field(name="user", value=str("\n".join(users)), inline=True)
        await ctx.send(embed=embed, content=None)
    
def setup(client):
    client.add_cog(level(client))
