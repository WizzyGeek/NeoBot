import discord
from discord.ext import commands

class Help(commands.Cog):
    """The Bot's Help Cog"""
    def __init__(self, bot):
        self.bot = bot
    
    @commands.group(name="help", aliases=['welp', 'jelp' ,'gelp', 'yelp'], description = "Welp?")
    async def welp(self, ctx): # TODO: HelpCommand class 
        """The first level Command for help"""
        # await ctx.send("under construction")
        embed = self.bot.Qembed(ctx, title="Help", content="Use `help <category>` for help on a category", Colour=1)
        embed.add_field(name="Moderation ", value="All moderation command", inline=False)
        embed.add_field(name="Music", value="Music commands", inline=False)
        embed.add_field(name="Font", value="Font changing commands", inline=False)
        embed.add_field(name="Fun", value="Fun commands", inline=False)
        embed.add_field(name="Utility", value="Utility commands ", inline=False)
        embed.add_field(name="Misc", value="Miscellaneous command", inline=False)
        await ctx.send(embed=embed)

def setup(bot):
    bot.remove_command("help")
    bot.add_cog(Help(bot))
    