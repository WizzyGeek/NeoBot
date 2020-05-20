import discord
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="help", aliases=['welp','jelp','gelp','yelp'], description = "Welp?")
    async def welp(self, ctx):
        ctx.send("under construction")
        
def setup(bot):
    bot.remove_command("help")
    bot.add_cog(Help(bot))