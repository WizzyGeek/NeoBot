import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="$")

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="help", aliases=['welp','jelp','gelp','yelp'], description = "Welp?")
    async def welp(self, ctx):
        author = ctx.author
        embed = discord.Embed(colour=0x00ff99)
        embed.set_author(name="Help")
        embed.add_field(name="`$help`", value="alias: welp \nshows this message.")
        embed.add_field(name="`$leaderboard`", value="alias: lb \nThe top users in the server")
        embed.add_field(name="`$rank`", value="alias: level\nGets anyones leveling stats like ```$rank @optional#0000```")
        embed.add_field(name="`$purge`", value="aliases: del, clear\nDeletes 5 or given number of messages like ```$purge 10```")
        embed.add_field(name="`$kick`", value="alias: begone \nKicks the user.```$kick @example#0000 optional reason```")
        embed.add_field(name="`$ban`", value="alias: banish\nBans the user similar to kick")
        embed.add_field(name="`$unban`", value="Unbans a user. Requires users name used as ```$unban example#0000```")
        embed.add_field(name="`$report`", value="See someone violating rules?```$report example#0000 reason```")
        embed.add_field(name="`$8ball`", value="alias: 8b\n usage: ```$8b test?```")
        embed.add_field(name="`$aware`", value="Educate the people about awarness")
        embed.add_field(name="`$Rainforest`", value="Rainforests are important!")
        embed.add_field(name="`$debate`", value="The spirit of debate")
        embed.add_field(name="`$10myths`", value="common myths on the enviroment")
        embed.add_field(name="`$climatechange`", value="climate change is real!")
        embed.add_field(name="`$sudo`", value="A group of command for admins.")
        channel = await author.create_dm()
        await channel.send(content=None, embed=embed)
        await ctx.send(content="Check your DMs", delete_after=5.0)
        return None
    
def setup(bot):
    bot.remove_command("help")
    bot.add_cog(Help(bot))