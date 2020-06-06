from discord.ext import commands

#from bot import korosensei


class Prefix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.prefixes = bot.prefixes
        self.DeleteTime = bot.DeleteTime

    @commands.command(name="prefix")
    async def prefix(self, ctx, *, prefix=None):
        main_prefix = self.prefixes[ctx.guild.id][0]
        if prefix is None:
            await ctx.send(f"The prefix is {main_prefix}")
        else:
            result = await self.bot.set_guild_prefixes(ctx.guild, prefix.split(","))
            if result is True:
                main_prefix = self.prefixes[ctx.guild.id][0]
                await ctx.send(f"The main prefix is set to {main_prefix}, all prefixes are {self.prefixes[ctx.guild.id]}")
            else:
                await ctx.send(
                    "Please ensure that all prefixes are seperated with `,`\n Also you can't have more than 10 prefixes",
                    delete_after=(self.DeleteTime + 3.0))


def setup(bot):
    bot.add_cog(Prefix(bot))
