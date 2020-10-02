import random
from sys import getsizeof

import discord
from discord.ext import commands, tasks

class Meme(commands.Cog):
    """COG TO FETCH MEMES FROM REDDIT"""
    def __init__(self, bot):
        self.bot = bot
        self.meme_done = []
        self.joke_done = []

    async def fetch_meme(self, ctx, SRs : list):
        """Fetch post with images or any post if none are available"""
        valid = []
        for post in self.bot.reddit_client.subreddit(random.choice(SRs)).hot(limit=25):
            if not post.stickied and not post.is_self and post.title not in self.meme_done and not post.over_18:
                valid.append(post)
        else:
            if len(valid) > 0:
                meme = random.choice(valid)
            else:
                meme = random.choice(list(self.bot.reddit_client.subreddit(random.choice(SRs)).rising(limit=25)))
        embed = discord.Embed(title=meme.title, timestamp=ctx.message.created_at, colour=ctx.author.colour, url=meme.shortlink).set_image(url=meme.url)
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)
        self.meme_done.append(meme.title)
        del valid

    @commands.command(name="meme")
    async def meme(self, ctx):
        """posts a meme"""
        SRs = ["memes", "dankmemes", "terriblefacebookmemes", "memeeconomy"]
        await self.fetch_meme(ctx, SRs)

    @commands.command(mame="comic")
    async def comic(self, ctx):

        SRs = ["fffffffuuuuuuuuuuuu", "comics"]
        await self.fetch_meme(ctx, SRs)

    async def fetch_joke(self, ctx, SRs):
        valid = []
        for post in self.bot.reddit_client.subreddit(random.choice(SRs)).hot(limit=25):
            if not post.stickied and post.is_self and post.title not in self.joke_done and not post.over_18:
                valid.append(post)
        else:
            if len(valid) > 0:
                joke = random.choice(valid)
            else:
                joke = random.choice(list(self.bot.reddit_client.subreddit(random.choice(SRs)).rising(limit=25)))

        embed = discord.Embed(title=joke.title + "\u200b", timestamp=ctx.message.created_at, colour=ctx.author.colour, description=joke.selftext, url=joke.shortlink).set_image(url=joke.url)
        await ctx.send(embed=embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url))
        self.joke_done.append(joke.title)
        del valid

    @commands.command(name="joke")
    async def joke(self, ctx):
        SRs = ["jokes"]
        await self.fetch_joke(ctx, SRs)

    @commands.command(name="dadjoke")
    async def dadjoke(self, ctx):
        SRs = ["dadjokes"]
        await self.fetch_joke(ctx, SRs)

    @tasks.loop(minutes=60.0)
    async def memory_optimizer(self):
        if getsizeof(self.meme_done) > 20971520: # 20 mb
            x = len(self.meme_done)
            del self.meme_done[x-(x/2):] # 10 mb ish
        if getsizeof(self.joke_done) > 20971520: # 20 mb
            x = len(self.joke_done)
            del self.joke_done[x-(x/2):]

def setup(bot):
    bot.add_cog(Meme(bot))
    credit = {
        "Entity": "Reddit",
        "Reason": "API"
    }
    bot.credits.append(credit)