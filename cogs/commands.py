import discord
from discord.ext import commands
import random



class utility(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="ping", aliases=["latency", "lag"])
    async def ping(self, ctx):
        await ctx.send('Pong! {0}'.format(client.latency))

    

def setup(bot):
    bot.add_cog(utility(bot))
