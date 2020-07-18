"""A cog to change font of a string."""
from discord.ext import commands


Smallcaps_alphabet = "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ1234567890"

Uppercase_fraktur = "𝔄𝔅ℭ𝔇𝔈𝔉𝔊ℌℑ𝔍𝔎𝔏𝔐𝔑𝔒𝔓𝔔ℜ𝔖𝔗𝔘𝔙𝔚𝔛𝔜ℨ"
Lowercase_fraktur = "𝔞𝔟𝔠𝔡𝔢𝔣𝔤𝔥𝔦𝔧𝔨𝔩𝔪𝔫𝔬𝔭𝔮𝔯𝔰𝔱𝔲𝔳𝔴𝔵𝔶𝔷1234567890"

Uppercase_boldfraktur = "𝕬𝕭𝕮𝕯𝕰𝕱𝕲𝕳𝕴𝕵𝕶𝕷𝕸𝕹𝕺𝕻𝕼𝕽𝕾𝕿𝖀𝖁𝖂𝖃𝖄𝖅"
Lowercase_boldfraktur = "𝖆𝖇𝖈𝖉𝖊𝖋𝖌𝖍𝖎𝖏𝖐𝖑𝖒𝖓𝖔𝖕𝖖𝖗𝖘𝖙𝖚𝖛𝖜𝖝𝖞𝖟1234567890"

double_uppercase = "𝔸𝔹ℂ𝔻𝔼𝔽𝔾ℍ𝕀𝕁𝕂𝕃𝕄ℕ𝕆ℙℚℝ𝕊𝕋𝕌𝕍𝕎𝕏𝕐ℤ"
double_lowercase = "𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡𝟘"

bold_fancy_lowercase = "𝓪𝓫𝓬𝓭𝓮𝓯𝓰𝓱𝓲𝓳𝓴𝓵𝓶𝓷𝓸𝓹𝓺𝓻𝓼𝓽𝓾𝓿𝔀𝔁𝔂𝔃1234567890"
bold_fancy_uppercase = "𝓐𝓑𝓒𝓓𝓔𝓕𝓖𝓗𝓘𝓙𝓚𝓛𝓜𝓝𝓞𝓟𝓠𝓡𝓢𝓣𝓤𝓥𝓦𝓧𝓨𝓩"

fancy_lowercase = "𝒶𝒷𝒸𝒹𝑒𝒻𝑔𝒽𝒾𝒿𝓀𝓁𝓂𝓃𝑜𝓅𝓆𝓇𝓈𝓉𝓊𝓋𝓌𝓍𝓎𝓏𝟣𝟤𝟥𝟦𝟧𝟨𝟩𝟪𝟫𝟢"
fancy_uppercase = "𝒜𝐵𝒞𝒟𝐸𝐹𝒢𝐻𝐼𝒥𝒦𝐿𝑀𝒩𝒪𝒫𝒬𝑅𝒮𝒯𝒰𝒱𝒲𝒳𝒴𝒵"


alphabet = dict(zip("abcdefghijklmnopqrstuvwxyz1234567890", range(0, 36)))
uppercase_alphabet = dict(zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ", range(0, 26)))
punctuation = dict(zip("§½!\"#¤%&/()=?`´@£$€{[]}\\^¨~'*<>|,.-_:", range(0, 37)))

space = " "

aesthetic_space = '\u3000'
aesthetic_punctuation = "§½！\"＃¤％＆／（）＝？`´＠£＄€｛［］｝＼＾¨~＇＊＜＞|，．－＿："
aesthetic_lowercase = "ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ１２３４５６７８９０"
aesthetic_uppercase = "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ"


def aesthetics(string):
    string = str(string)
    returnthis = ""
    for word in string:
        for letter in word:
            if letter in alphabet:
                returnthis += aesthetic_lowercase[alphabet[letter]]
            elif letter in uppercase_alphabet:
                returnthis += aesthetic_uppercase[uppercase_alphabet[letter]]
            elif letter in punctuation:
                returnthis += aesthetic_punctuation[punctuation[letter]]
            elif letter == space:
                returnthis += aesthetic_space
            else:
                returnthis += letter
    return returnthis


def convert(string: str, uppercase: list, lowercase: list):
    string = str(string)
    returnthis = ""
    for word in string:
        for letter in word:
            if letter in alphabet:
                returnthis += lowercase[alphabet[letter]]
            elif letter in uppercase_alphabet:
                returnthis += uppercase[uppercase_alphabet[letter]]
            elif letter == space:
                returnthis += " "
            else:
                returnthis += letter
    return returnthis


# def double_font(string):
#     string = str(string)
#     returnthis = ""
#     for word in string:
#         for letter in word:
#             if letter in alphabet:
#                 returnthis += double_lowercase[alphabet[letter]]
#             elif letter in uppercase_alphabet:
#                 returnthis += double_uppercase[uppercase_alphabet[letter]]
#             elif letter == space:
#                 returnthis += " "
#             else:
#                 returnthis += letter
#     return returnthis


# def fraktur(string):
#     string = str(string)
#     returnthis = ""
#     for word in string:
#         for letter in word:
#             if letter in alphabet:
#                 returnthis += Lowercase_fraktur[alphabet[letter]]
#             elif letter in uppercase_alphabet:
#                 returnthis += Uppercase_fraktur[uppercase_alphabet[letter]]
#             elif letter == space:
#                 returnthis += " "
#             else:
#                 returnthis += letter
#     return returnthis


# def bold_fraktur(string):
#     string = str(string)
#     returnthis = ""
#     for word in string:
#         for letter in word:
#             if letter in alphabet:
#                 returnthis += Lowercase_boldfraktur[alphabet[letter]]
#             elif letter in uppercase_alphabet:
#                 returnthis += Uppercase_boldfraktur[uppercase_alphabet[letter]]
#             elif letter == space:
#                 returnthis += " "
#             else:
#                 returnthis += letter
#     return returnthis


# def fancy(string):
#     string = str(string)
#     returnthis = ""
#     for word in string:
#         for letter in word:
#             if letter in alphabet:
#                 returnthis += fancy_lowercase[alphabet[letter]]
#             elif letter in uppercase_alphabet:
#                 returnthis += fancy_uppercase[uppercase_alphabet[letter]]
#             elif letter == space:
#                 returnthis += " "
#             else:
#                 returnthis += letter
#     return returnthis


# def bold_fancy(string):
#     string = str(string)
#     returnthis = ""
#     for word in string:
#         for letter in word:
#             if letter in alphabet:
#                 returnthis += bold_fancy_lowercase[alphabet[letter]]
#             elif letter in uppercase_alphabet:
#                 returnthis += bold_fancy_uppercase[uppercase_alphabet[letter]]
#             elif letter == space:
#                 returnthis += " "
#             else:
#                 returnthis += letter
#     return returnthis


def smallcaps(string):
    string = str(string)
    returnthis = ""
    for word in string:
        for letter in word:
            if letter in alphabet:
                returnthis += Smallcaps_alphabet[alphabet[letter]]
            else:
                returnthis += letter
    return returnthis


class Font(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='aesthetics', aliases=['ae'])
    async def _aesthetics(self, ctx, *, sentence: commands.clean_content):
        """Change text to aesthetic."""
        await ctx.send(aesthetics(sentence))

    @commands.command(name='fraktur')
    async def _fraktur(self, ctx, *, sentence: commands.clean_content):
        """Change text to fraktur."""
        await ctx.send(convert(sentence, Uppercase_fraktur, Lowercase_fraktur))

    @commands.command(name='boldfaktur')
    async def _boldfaktur(self, ctx, *, sentence: commands.clean_content):
        """Change text to fraktur but bold."""
        await ctx.send(convert(sentence, Uppercase_boldfraktur, Lowercase_boldfraktur))

    @commands.command(name='fancy', aliases=['ff'])
    async def _fancy(self, ctx, *, sentence: commands.clean_content):
        """Change text to fancy."""
        await ctx.send(convert(sentence, fancy_uppercase, fancy_lowercase))

    @commands.command(name='boldfancy', aliases=['bf'])
    async def _bold_fancy(self, ctx, *, sentence: commands.clean_content):
        """Change text to fancy but bold."""
        await ctx.send(convert(sentence, bold_fancy_uppercase, bold_fancy_lowercase))

    @commands.command(name='double', aliases=['ds'])
    async def _doublestruck(self, ctx, *, sentence: commands.clean_content):
        """Change text to double."""
        await ctx.send(convert(sentence, double_uppercase, double_lowercase))

    @commands.command(name='smallcaps', aliases=['scap'])
    async def _smallcaps(self, ctx, *, sentence: commands.clean_content):
        """Change text to smallcaps."""
        await ctx.send(smallcaps(sentence))


def setup(bot: commands.Bot) -> None:
    """Into pan goes the cog."""
    bot.add_cog(Font(bot))
