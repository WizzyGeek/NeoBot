import shlex
import discord
from discord.ext import commands

async def to_keycap(c):
    return '\N{KEYCAP TEN}' if c == 10 else str(c) + '\u20e3'

class utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx: commands.Context) -> None:
        """
        used to check if the bot is alive
        """
        await ctx.send(embed=self.bot.Qembed(ctx, title="pong!", content="Bot latency is {0:.2f}ms".format(self.bot.latency * 1000)))

    @commands.command(no_pm=True)
    async def poll(self, ctx: commands.Context, *, question: str) -> None:
        """
        Quick and easy yes/no poll, for multiple answers, see !quickpoll
        """
        msg: discord.Message = await ctx.send(embed = self.bot.Qembed(ctx, title="Poll", content=question))
        try:
            await ctx.message.delete()
        except:
            pass
        yes_thumb: str = "👍"
        no_thumb: str = "👎"
        await msg.add_reaction(yes_thumb)
        await msg.add_reaction(no_thumb)

    @commands.command(no_pm=True)
    async def quickpoll(self, ctx: commands.Context, *, questions_and_choices: str):
        """
        delimit questions and answers by either | or , 
        supports up to 10 choices
        """
        if "|" in questions_and_choices:
            delimiter = "|"
        elif "," in questions_and_choices:
            delimiter = ","
        else:
            delimiter = None
        if delimiter is not None:
            questions_and_choices = questions_and_choices.split(delimiter)
        else:
            questions_and_choices = shlex.split(questions_and_choices)

        if len(questions_and_choices) < 3:
            return await ctx.send('Need at least 1 question with 2 choices.')
        elif len(questions_and_choices) > 11:
            return await ctx.send('You can only have up to 10 choices.')

        perms = ctx.channel.permissions_for(ctx.guild.me)
        if not (perms.read_message_history or perms.add_reactions):
            return await ctx.send('Need Read Message History and Add Reactions permissions.')

        question = questions_and_choices[0]
        choices = [(await to_keycap(e), v) for e, v in enumerate(questions_and_choices[1:], 1)]

        try:
            await ctx.message.delete()
        except:
            pass

        fmt = '{0}\n\n{1}'
        answer = '\n'.join('%s| %s' % t for t in choices)
        embed: discord.Embed = self.bot.Qembed(
            ctx, title="Poll", content=fmt.format(question.replace("@", "@\u200b"), answer.replace("@", "@\u200b")))
        poll = await ctx.send(embed=embed)
        for choice in choices:
            await poll.add_reaction(choice[0])

    @commands.command()
    async def avatar(self, ctx: commands.Context, user: discord.Member = None):
        if user is None:
            user: discord.Member = ctx.author
        embed: discord.Embed = discord.Embed(title=f"{user.name}\'s Avatar'", colour=ctx.author.colour).set_image(url = str(user.avatar_url)).timestamp
        return await ctx.send(embed=embed)
    
    @commands.command()
    async def about(self, ctx: commands.Context):
        await ctx.send(str(self.bot.description))

    # TODO:: [Use self.bot.credits]
    # @commands.command(hidden=True)
    # async def credits(self, ctx: commands.Context):
    #     await ctx.send(
    #         embed=discord.Embed(
    #             colour=discord.Colour.blue(),
    #             title="Credits",
    #             description="Anvit#4806\nvladdd#0001\n & Authors of other bots and dependecies."))

    @commands.group(name="config")
    async def config(self, ctx: commands.Context):
        pass

    @config.command(name="modlog")
    async def modlog(self, ctx: commands.Context, channel: discord.TextChannel):
        """Set the channel to log moderation action"""
        if not channel:
            return await ctx.send(embed=self.bot.Qembed(colour=3, title="Error", content="Could not ind the specifie channel"))
        channel_id = channel.id
        async with self.bot.DbPool.acquire() as conn:
            conn.execute("""
                INSERT INTO server(gid, modlog)
                VALUES($1, $2)
                ON CONFLICT (gid)
                DO UPDATE SET modlog = $2;
                """, ctx.guild.id, channel_id)
        await ctx.send(f"Set the Mod Log channel to {channel.name}")
    
    @config.command(name="welcome", hidden=False)
    async def welcome(self, ctx: commands.Context, channel: discord.TextChannel):
        """Set the channel to welcome users, cannot change message format currently"""
        if not channel:
            return await ctx.send(embed=self.bot.Qembed(colour=3, title="Error", content="Could not ind the specifie channel"))
        channel_id = channel.id
        async with self.bot.DbPool.acquire() as conn:
            conn.execute("""
                INSERT INTO server(gid, welchannel)
                VALUES($1, $2)
                ON CONFLICT (gid)
                DO UPDATE SET welchannel = $2;
                """, ctx.guild.id, channel_id)
        await ctx.send(f"Set the welcome channel to {channel.name}")

def setup(bot: commands.Bot) -> None:
    """Cog setup function."""
    bot.add_cog(utility(bot))
