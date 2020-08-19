from discord.ext import commands
import discord

#from bot import korosensei


class Prefix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="prefix")
    async def prefix(self, ctx: commands.Context):
        if not ctx.invoked_subcommand:
            prefixes = self.bot.get_guild_prefixes(ctx.guild)
            await ctx.send_embed(title=f"Prefixes", description="".join([f"{pre}\n" for pre in prefixes][1:]), colour=discord.Colour.blue())

def setup(bot: commands.Bot) -> None:
    """Cog setup function."""
    bot.add_cog(Prefix(bot))