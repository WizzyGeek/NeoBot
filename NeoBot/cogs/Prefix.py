from discord.ext import commands

#from bot import korosensei


class Prefix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.prefixes = bot.prefixes
        self.DeleteTime = bot.DeleteTime

    @commands.command(name="prefix")
    async def prefix(self, ctx, *, prefix=None):
        """Change the prefix or view all prefixes of the bot."""
        main_prefix = self.prefixes[ctx.guild.id][0]
        if prefix is None:
            await ctx.send(
                embed=self.bot.Qembed(
                    ctx,
                    title=f"Main prefix - {main_prefix}",
                    content=f"All prefixes are: \n{n.join(fmt.format(X[0], X[1]) for X in enumerate(self.prefixes[ctx.guild.id], start=1))}"))
        else:
            prefixes = prefix.split(",")
            for p in prefixes:
                p = p.lstrip()
            result = await self.bot.set_guild_prefixes(ctx.guild, prefixes)
            if result is True:
                main_prefix = self.prefixes[ctx.guild.id][0]
                n = "\n"
                fmt = "{0}. `{1}`"
                await ctx.send(embed=self.bot.Qembed(ctx, title=f"Main prefix - {main_prefix}", content=f"All prefixes are: \n{n.join(fmt.format(X[0], X[1]) for X in enumerate(self.prefixes[ctx.guild.id], start=1))}"))
            else:
                await ctx.send(
                    "Please ensure that all prefixes are seperated with `,`\n Also you can't have more than 10 prefixes",
                    delete_after=(self.DeleteTime + 3.0))


def setup(bot: commands.Bot) -> None:
    """Cog setup function."""
    bot.add_cog(Prefix(bot))
