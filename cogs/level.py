import discord
from discord.ext import commands
from utils.utility import LevelsQuery, ranking

client = commands.Bot(command_prefix="$")

class level(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.command(name="level", aliases=["levelquery"], description="returns a users level or you own")
    async def UserLevelQuery(self, ctx, user=None):
        if user == None:
            user = ctx.author
        QueryResult = await LevelsQuery(user)
        XP = QueryResult[0]
        lvl = QueryResult[1]
        rank = QueryResult[2]
        embed = discord.Embed(title=f"{str(user)}'s level info", description=f"**Rank**: {rank}\n**lvl**: {lvl}\n**XP**: {XP}", colour=discord.Color.dark_blue())
        await ctx.send(embed=embed)
        return
        
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
