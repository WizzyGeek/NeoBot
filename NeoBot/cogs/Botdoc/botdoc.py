# botdoc
# Documentation generating cog for discord.py

import os
from discord.ext import commands
import logging

logger: logging.Logger = logging.getLogger(__name__)

def _h(num, text):
    """ Returns a h1-h6 string """
    header = ''
    for i in range(num):
        header += '#'
    return f'{header} {text}\n\n'


def _text(text):
    """ Returns normal text string """
    return f'{text}\n\n'


def _local_toc(text):
    """ Returns a single item for an unordered list with link to other section """
    return f' * [{text}](#{text})\n'


def _global_toc(cog, text):
    """ Returns a single item for an unordered list with link to other file in same folder """
    return f' * [{text}]({cog}.md#{text})\n'


def _code_block(text):
    """ Returns a code block string """
    return f'```\n{text}\n```\n\n'


def _inline_code(text):
    """ Returns an inline code string """
    return f'`{text}`'


def _make_docs_dir(bot):
    """ Makes docs dir at same level as the bots main.py file """
    cwd = os.path.abspath(os.getcwd())
    out_dir = f'{cwd}/docs'
    os.makedirs(out_dir, exist_ok=True)
    logger.info(f"Created {out_dir} directory")
    return out_dir


def _generate_index(bot, out_dir):
    """ Generates an index file with links to all cog doc files """
    out_filename = f'{out_dir}/index.md'
    out = open(out_filename, "w")
    # Title
    ret = _h(1, "Index")
    # TOC
    for cog in bot.cogs:
        ret += _h(2, cog)
        for command in bot.get_cog(cog).get_commands():
            ret += _global_toc(cog, command)
        ret += '\n'
    out.write(ret)
    out.close()
    logger.info("Outputted index to %s", out_filename)


def _generate_usage(bot, command):
    """ Generates a string of how to use a command """
    temp = f'!b '  # TODO
    # Aliases
    if len(command.aliases) == 0:
        temp += f'{command.name}'
    elif len(command.aliases) == 1:
        temp += f'[{command.name}|{command.aliases[0]}]'
    else:
        t = '|'.join(command.aliases)
        temp += f'[{command.name}|{t}]'
    # Parameters
    params = f' '
    for param in command.clean_params:
        params += f'<{command.clean_params[param]}> '
    temp += f'{params}'
    return _text(_inline_code(temp))


def _generate_cog_docs(bot, out_dir):
    """ Generates a file of documentation for a cog """
    # Run thru the cogs
    for cog in bot.cogs:
        # Make cog doc file
        out_filename = f'{out_dir}/{cog}.md'
        out = open(out_filename, "w")
        # Title
        ret = _h(1, cog)
        # TOC
        for command in bot.get_cog(cog).get_commands():
            ret += _local_toc(command)
        # Details
        ret += '\n'
        for command in bot.get_cog(cog).get_commands():
            # Compile docs
            ret += _h(2, _inline_code(command))
            if command.description is not None:
                ret += _text(command.description)
            else:
                ret += "No description."
            if command.help is not None:
                ret += _text(command.help)
            ret += _h(3, "Syntax")
            ret += _generate_usage(bot, command)
            ret += _text("---")
        # Link back to index
        ret += _global_toc("index", "Index")
        # Output to file
        out.write(ret)
        out.close()
        logger.info("Outputted to %s", out_filename)


class Docs(commands.Cog):
    """ botdoc auto generates documentation for cogs/commands """

    def __init__(self, bot):
        self.bot = bot
        out_dir = _make_docs_dir(bot)
        _generate_index(bot, out_dir)
        _generate_cog_docs(bot, out_dir)


# Cog setup
def setup(bot):
    bot.add_cog(Docs(bot))
    credit = {
        "Entity": "[Zed Chance](https://github.com/zedchance)",
        "Reason": "Botdocs Cog"
    }
    bot.credit.append(credit)


if __name__ == '__main__':
    logger.info(f'Add cogs.botdoc.botdoc to your cogs list')
