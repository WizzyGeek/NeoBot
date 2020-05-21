from discord.ext import commands

#from bot import korosensei

class Prefix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.prefixes = bot.prefixes
        
    @commands.command(name="prefix")
    async def prefix(self, ctx, prefix=None):
        main_prefix = self.prefixes[ctx.guild.id][0]
        if prefix is None:
            await ctx.send(f"The prefix is {main_prefix}")
        else:
            await ctx.send("-------Under construction!-------")
        
def setup(bot):
    bot.add_cog(Prefix(bot))