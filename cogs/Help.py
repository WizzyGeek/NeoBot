import discord
from discord.ext import commands

class Help(commands.Cog):
    """The Bot's Help Cog"""
    def __init__(self, bot):
        self.bot = bot
        self.prefixes = bot.prefixes

    @commands.group(name="help", aliases=['welp', 'jelp' ,'gelp', 'yelp'], description = "Welp?")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help(self, ctx): # TODO: HelpCommand class 
        """The first level Command for help"""
        # await ctx.send("under construction")
        if ctx.invoked_subcommand is None:
            main_prefix = self.prefixes[ctx.guild.id][0]
            embed = self.bot.Qembed(ctx, title="Help", content="Use `help <category>` for help on a category", Colour=1)
            embed.add_field(name=":hammer: Moderation ", value=f"`{main_prefix}help moderation`\nAll moderation command", inline=True)
            embed.add_field(name=":musical_note: Music", value=f"`{main_prefix}help music`\nMusic commands", inline=True)
            embed.add_field(name=":abcd: Font", value=f"`{main_prefix}help font`\nFont changing commands", inline=True)
            embed.add_field(name=":smile: Fun", value=f"`{main_prefix}help fun`\nFun commands", inline=True)
            embed.add_field(name=":hammer_pick: Utility", value=f"`{main_prefix}help utility`\nUtility commands ", inline=True)
            embed.add_field(name=":wrench: Misc", value=f"`{main_prefix}help misc`\nMiscellaneous command", inline=True)
            await ctx.send(embed=embed)

    @help.error
    async def help_error(self, ctx, error):
        """Cooldown handler"""
        if isinstance(error, commands.errors.CommandOnCooldown):
            await ctx.send(
                embed=self.bot.Qembed(ctx, title="Slow Down!",
                                      content=f"""This command has a 5 second cooldown for
                                                  each user. Try again in `{error.retry_after} seconds`"""))


    @help.command(name="moderation")
    async def mod_help(self, ctx):
        main_prefix = self.prefixes[ctx.guild.id][0]
        embed = self.bot.Qembed(ctx, title="Help Moderation")
        embed.add_field(name="warn", value=f"warn an user \n`{main_prefix}warn @example#0000 raider`", inline=True)
        embed.add_field(name="unban", value=f"Unban an user \n`{main_prefix}unban 12345678901`\n`{main_prefix}unban example#0000`", inline=True)
        embed.add_field(name="clear", value=f"Clear the specified messages `{main_prefix}purge` to purge 5 messages\n`{main_prefix}clear 200`", inline=True)
        embed.add_field(name="kick", value=f"Kick an user\n`{main_prefix}kick @example#0000 raider`", inline=True)
        embed.add_field(name="ban", value=f"Ban an user\n`{main_prefix}ban @example#0000 raider`", inline=True)
        embed.add_field(name="userinfo", value=f"Get info on an user\n`{main_prefix}uinfo @example#0000`", inline=True)
        embed.add_field(name="guildinfo", value=f"Info on the server\n`{main_prefix}ginfo`", inline=True)
        await ctx.author.send(embed=embed)
        await ctx.message.add_reaction("✅")
        await ctx.send(f"{ctx.author.mention} check your DMs", delete_after=self.bot.DeleteTime)

def setup(bot):
    bot.remove_command("help")
    bot.add_cog(Help(bot))
    