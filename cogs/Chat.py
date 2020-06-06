import pprint
import random
from difflib import SequenceMatcher

# import sys
# from pathlib import Path

# file = Path(__file__).resolve() # i appreciate pep 8 but this is ugly, switch to setup.py in future
# parent, root = file.parent, file.parents[1]
# sys.path.append(str(root))

import praw
from discord.ext import commands

# ignore error here this is not the top level script
# from bot import Bot


class Chat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['c', 'ch'])
    async def chat(self, ctx, *, you):
        reply = str(self.grab_reply(you))
        await ctx.send(reply)
        #logger.info("Chat command requested!")
    #----------------------------------------#

    @staticmethod
    def similar(a, b):
        return SequenceMatcher(None, a, b).ratio()
    #----------------------------------------#

    def grab_reply(self, question):
        reddit = self.bot.reddit_client
        x = 0
        submission_ids = []
        for results in reddit.subreddit('all').search(question):
            id = results.id
            title = results.title
            comments = results.num_comments
            if comments > 1 and Chat.similar(question, title) > .8:
                submission_ids.append(id)
                x += 1
            if x >= 20:
                break
        if len(submission_ids) == 0:
            return "I have no idea"
        submission = reddit.submission(
            id=submission_ids[random.randint(0, len(submission_ids)-1)])
        comment_list = []
        x = 0
        for top_level_comment in submission.comments:
            body = top_level_comment.body
            comment_list.append(body)
            x += 1
            if x >= 5:
                break
        if len(comment_list) == 0:
            return "I have no clue"
        return comment_list[random.randint(0, len(comment_list)-1)]
    #----------------------------------------#

def setup(bot):
    bot.add_cog(Chat(bot))