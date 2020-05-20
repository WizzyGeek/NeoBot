import random
import re
import json

from discord.ext import commands
import discord

'''Module for fun/meme commands'''

class Fun:
    def __init__(self, bot):
        self.bot = bot
        self.regionals = {'a': '\N{REGIONAL INDICATOR SYMBOL LETTER A}', 'b': '\N{REGIONAL INDICATOR SYMBOL LETTER B}',
                          'c': '\N{REGIONAL INDICATOR SYMBOL LETTER C}',
                          'd': '\N{REGIONAL INDICATOR SYMBOL LETTER D}', 'e': '\N{REGIONAL INDICATOR SYMBOL LETTER E}',
                          'f': '\N{REGIONAL INDICATOR SYMBOL LETTER F}',
                          'g': '\N{REGIONAL INDICATOR SYMBOL LETTER G}', 'h': '\N{REGIONAL INDICATOR SYMBOL LETTER H}',
                          'i': '\N{REGIONAL INDICATOR SYMBOL LETTER I}',
                          'j': '\N{REGIONAL INDICATOR SYMBOL LETTER J}', 'k': '\N{REGIONAL INDICATOR SYMBOL LETTER K}',
                          'l': '\N{REGIONAL INDICATOR SYMBOL LETTER L}',
                          'm': '\N{REGIONAL INDICATOR SYMBOL LETTER M}', 'n': '\N{REGIONAL INDICATOR SYMBOL LETTER N}',
                          'o': '\N{REGIONAL INDICATOR SYMBOL LETTER O}',
                          'p': '\N{REGIONAL INDICATOR SYMBOL LETTER P}', 'q': '\N{REGIONAL INDICATOR SYMBOL LETTER Q}',
                          'r': '\N{REGIONAL INDICATOR SYMBOL LETTER R}',
                          's': '\N{REGIONAL INDICATOR SYMBOL LETTER S}', 't': '\N{REGIONAL INDICATOR SYMBOL LETTER T}',
                          'u': '\N{REGIONAL INDICATOR SYMBOL LETTER U}',
                          'v': '\N{REGIONAL INDICATOR SYMBOL LETTER V}', 'w': '\N{REGIONAL INDICATOR SYMBOL LETTER W}',
                          'x': '\N{REGIONAL INDICATOR SYMBOL LETTER X}',
                          'y': '\N{REGIONAL INDICATOR SYMBOL LETTER Y}', 'z': '\N{REGIONAL INDICATOR SYMBOL LETTER Z}',
                          '0': '0⃣', '1': '1⃣', '2': '2⃣', '3': '3⃣',
                          '4': '4⃣', '5': '5⃣', '6': '6⃣', '7': '7⃣', '8': '8⃣', '9': '9⃣', '!': '\u2757',
                          '?': '\u2753'}
        self.emoji_reg = re.compile(r'<:.+?:([0-9]{15,21})>')
        self.ball = ['● It is certain.',
            '● It is decidedly so.',
            '● Without a doubt.',
            '● Yes - definitely.',
            '● You may rely on it.',
            '● As I see it, yes.',
            '● Most likely.',
            '● Outlook good.',
            '● Yes.',
            '● Signs point to yes.',
            '● Reply hazy, try again.',
            '● Ask again later.',
            '● Better not tell you now.',
            '● Cannot predict now.',
            '● Concentrate and ask again.',
            '● Don\'t count on it.',
            '● My reply is no.',
            '● My sources say no.',
            '● Outlook not so good.',
            '● Very doubtful.',
            ]

    emoji_dict = {
        'a': ['🇦', '🅰', '🍙', '🔼', '4⃣'],
        'b': ['🇧', '🅱', '8⃣'],
        'c': ['🇨', '©', '🗜'],
        'd': ['🇩', '↩'],
        'e': ['🇪', '3⃣', '📧', '💶'],
        'f': ['🇫', '🎏'],
        'g': ['🇬', '🗜', '6⃣', '9⃣', '⛽'],
        'h': ['🇭', '♓'],
        'i': ['🇮', 'ℹ', '🚹', '1⃣'],
        'j': ['🇯', '🗾'],
        'k': ['🇰', '🎋'],
        'l': ['🇱', '1⃣', '🇮', '👢', '💷'],
        'm': ['🇲', 'Ⓜ', '📉'],
        'n': ['🇳', '♑', '🎵'],
        'o': ['🇴', '🅾', '0⃣', '⭕', '🔘', '⏺', '⚪', '⚫', '🔵', '🔴', '💫'],
        'p': ['🇵', '🅿'],
        'q': ['🇶', '♌'],
        'r': ['🇷', '®'],
        's': ['🇸', '💲', '5⃣', '⚡', '💰', '💵'],
        't': ['🇹', '✝', '➕', '🎚', '🌴', '7⃣'],
        'u': ['🇺', '⛎', '🐉'],
        'v': ['🇻', '♈', '☑'],
        'w': ['🇼', '〰', '📈'],
        'x': ['🇽', '❎', '✖', '❌', '⚒'],
        'y': ['🇾', '✌', '💴'],
        'z': ['🇿', '2⃣'],
        '0': ['0⃣', '🅾', '0⃣', '⭕', '🔘', '⏺', '⚪', '⚫', '🔵', '🔴', '💫'],
        '1': ['1⃣', '🇮'],
        '2': ['2⃣', '🇿'],
        '3': ['3⃣'],
        '4': ['4⃣'],
        '5': ['5⃣', '🇸', '💲', '⚡'],
        '6': ['6⃣'],
        '7': ['7⃣'],
        '8': ['8⃣', '🎱', '🇧', '🅱'],
        '9': ['9⃣'],
        '?': ['❓'],
        '!': ['❗', '❕', '⚠', '❣'],
        'combination': [['cool', '🆒'],
                        ['back', '🔙'],
                        ['soon', '🔜'],
                        ['free', '🆓'],
                        ['end', '🔚'],
                        ['top', '🔝'],
                        ['abc', '🔤'],
                        ['atm', '🏧'],
                        ['new', '🆕'],
                        ['sos', '🆘'],
                        ['100', '💯'],
                        ['loo', '💯'],
                        ['zzz', '💤'],
                        ['...', '💬'],
                        ['ng', '🆖'],
                        ['id', '🆔'],
                        ['vs', '🆚'],
                        ['wc', '🚾'],
                        ['ab', '🆎'],
                        ['cl', '🆑'],
                        ['ok', '🆗'],
                        ['up', '🆙'],
                        ['10', '🔟'],
                        ['11', '⏸'],
                        ['ll', '⏸'],
                        ['ii', '⏸'],
                        ['tm', '™'],
                        ['on', '🔛'],
                        ['oo', '🈁'],
                        ['!?', '⁉'],
                        ['!!', '‼'],
                        ['21', '📅'],
                        ]
    }

    # used in textflip
    text_flip = {}
    char_list = "!#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}"
    alt_char_list = "{|}zʎxʍʌnʇsɹbdouɯlʞɾᴉɥƃɟǝpɔqɐ,‾^[\]Z⅄XMΛ∩┴SɹQԀONW˥ʞſIHפℲƎpƆq∀@¿<=>;:68ㄥ9ϛㄣƐᄅƖ0/˙-'+*(),⅋%$#¡"[::-1]
    for idx, char in enumerate(char_list):
        text_flip[char] = alt_char_list[idx]
        text_flip[alt_char_list[idx]] = char
    #----------------------------------------#
    # used in [p]react, checks if it's possible to react with the duper string or not
    def has_dupe(duper):
        collect_my_duper = list(filter(lambda x: x != '⃣', duper))  #   ⃣ appears twice in the number unicode thing, so that must be stripped
        return len(set(collect_my_duper)) != len(collect_my_duper)
    #----------------------------------------#
    # used in [p]react, replaces e.g. 'ng' with '🆖'
    def replace_combos(react_me):
        for combo in Fun.emoji_dict['combination']:
            if combo[0] in react_me:
                react_me = react_me.replace(combo[0], combo[1], 1)
        return react_me
    #----------------------------------------#
    # used in [p]react, replaces e.g. 'aaaa' with '🇦🅰🍙🔼'
    def replace_letters(react_me):
        for char in "abcdefghijklmnopqrstuvwxyz0123456789!?":
            char_count = react_me.count(char)
            if char_count > 1:  # there's a duplicate of this letter:
                if len(Fun.emoji_dict[char]) >= char_count:  # if we have enough different ways to say the letter to complete the emoji chain
                    i = 0
                    while i < char_count:  # moving goal post necessitates while loop instead of for
                        if Fun.emoji_dict[char][i] not in react_me:
                            react_me = react_me.replace(char, Fun.emoji_dict[char][i], 1)
                        else:
                            char_count += 1  # skip this one because it's already been used by another replacement (e.g. circle emoji used to replace O already, then want to replace 0)
                        i += 1
            else:
                if char_count == 1:
                    react_me = react_me.replace(char, Fun.emoji_dict[char][0])
        return react_me
    #----------------------------------------#
    @commands.command(aliases=['8ball', '8b', "luckyball"])
    async def _bball(self, ctx, *, question):
        ans = ['● It is certain.',
            '● It is decidedly so.',
            '● Without a doubt.',
            '● Yes - definitely.',
            '● You may rely on it.',
            '● As I see it, yes.',
            '● Most likely.',
            '● Outlook good.',
            '● Yes.',
            '● Signs point to yes.',
            '● Reply hazy, try again.',
            '● Ask again later.',
            '● Better not tell you now.',
            '● Cannot predict now.',
            '● Concentrate and ask again.',
            '● Don\'t count on it.',
            '● My reply is no.',
            '● My sources say no.',
            '● Outlook not so good.',
            '● Very doubtful.',
            ]
        await ctx.send(f"{random.choice(ans)}")
    #----------------------------------------#
    @commands.command(pass_context=True, aliases=['pick'])
    async def choose(self, ctx, *, choices: str):
        """Choose randomly from the options you give. [p]choose this | that"""
        await ctx.send(self.bot.bot_prefix + 'I choose: ``{}``'.format(random.choice(choices.split("|"))))
    #----------------------------------------#
    @commands.command(pass_context=True, aliases=['lmgtfy', 'google'])
    async def l2g(self, ctx, *, query: str):
        """Creates a lmgtfy link. Ex: [p]l2g how do i become cool."""
        await ctx.send(f'http://lmgtfy.com/?q={query.replace(" ", "+")}')
        
    @l2g.error
    async def l2g_error(ctx, err):
        if isinstance(err, commands.MissingRequiredArgument):
            ctx.send("Provide a sting to search.")
    #----------------------------------------#            
    @commands.command(pass_context=True, aliases="novowels")
    async def vowelreplace(self, ctx, replace, *, msg):
        """Replaces all vowels in a word with a letter"""
        result = ""
        for letter in msg:
            if letter.lower() in "aeiou":
                result += replace
            else:
                result += letter
        await ctx.message.delete()
        await ctx.send(result)
    #----------------------------------------# 
    @commands.command(pass_context=True)
    async def dice(self, ctx, dice=1, faces=6):
        """Roll dice. Optionally input # of dice and # of sides. Ex: [p]dice 5 12"""
        res = []
        embed = discord.Embed(title="**Dice  rolled..**")
        if faces < 9:
            for i in range(dice):
                embed.add_field(title = f"Die {i+1}", desc=f'{self.regionals[random.randint(1, faces)]}')
        else:
            for i in range(dice):
                embed.add_field(title = f"Die {i+1}", desc=str(random.randint(1, faces)))
      
        await ctx.send(embed=embed)
    #----------------------------------------#
    @commands.command(pass_context=True)
    async def textflip(self, ctx, *, msg):
        """Flip given text."""
        result = ""
        for char in msg:
            if char in self.text_flip:
                result += self.text_flip[char]
            else:
                result += char
        await ctx.message.edit(content=result[::-1])  # slice reverses the string
    #----------------------------------------#
    @commands.command(pass_context=True, aliases=['emojify'])
    async def regional(self, ctx, *, msg):
        """Replace letters with regional indicator emojis"""
        await ctx.message.delete()
        msg = list(msg)
        regional_list = [self.regionals[x.lower()] if x.isalnum() or x in ["!", "?"] else x for x in msg]
        regional_output = '\u200b'.join(regional_list)
        await ctx.send(regional_output)
        
    @regional.error
    async def regional_error(ctx, err):
        if isinstance(err, commands.MissingRequiredArgument):
            ctx.send("Give me a string (text) to emojify.")
    #----------------------------------------#
    @commands.command(pass_context=True)
    async def space(self, ctx, spaces=1, *, msg):
        """Add n spaces between each letter. Ex: [p]space 2 thicc"""
        await ctx.message.delete()
        spaced_message = spaces.join(list(msg))
        await ctx.send(spaced_message)
        
    @space.error
    async def space_error(ctx, err):
        if isinstance(err, commands.MissingRequiredArgument):
            ctx.send("Give me a string (text) to space out.")
    #----------------------------------------#
     

def setup(bot):
    bot.add_cog(Fun(bot))