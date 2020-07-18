from .Classes import Config, NeoContext
from typing import List as _List
from .errors import ConnectionAlreadyAcquiredError

def _prefix_callable(bot, msg) -> _List[str]:
    user_id: int = bot.user.id
    base: List[str] = ["<@!{}> ".format(user_id), "<@{}> ".format(user_id)]
    if msg.guild is None:
        base.append(".")
        base.append("$")
    else:
        base.extend(bot.prefixes.get(msg.guild.id, ["$", "."]))
    return base