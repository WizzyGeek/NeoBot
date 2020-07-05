from .Classes import Config
from typing import List

def _prefix_callable(bot, msg) -> List[str]:
    user_id: int = bot.user.id
    base: List[str] = ["<@!{}> ".format(user_id), "<@{}> ".format(user_id)]
    if msg.guild is None:
        base.append(".")
        base.append("$")
    else:
        base.extend(bot.prefixes.get(msg.guild.id, ["$", "."]))
    return base