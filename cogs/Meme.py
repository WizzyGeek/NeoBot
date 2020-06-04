import random

import discord
from discord.ext import commands

class Meme(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def fetch_meme(self, ctx, SRs : list):
        meme = random.choice([post for post in self.bot.reddit_client.subreddit(random.choice(SRs)).rising(limit=15) if not post.stickied and not post.is_self])
        embed = discord.Embed(title=meme.title, timestamp=ctx.message.created_at, colour=ctx.author.colour).set_image(url=str(meme.url))
        await ctx.send(embed=embed.set_footer(text=ctx.author, icon_url = ctx.author.avatar_url))

    @commands.command(name="meme")
    async def meme(self, ctx):
        SRs = ["memes", "dankmemes", "terriblefacebookmemes", "memeeconomy"]
        self.fetch_meme(ctx, SRs)

    @commands.command(mame="comic")
    async def comic(self, ctx):
        SRs = ["fffffffuuuuuuuuuuuu", "comics"]
        self.fetch_meme(ctx, SRs)


def setup(bot):
    bot.add_cog(Meme(bot))