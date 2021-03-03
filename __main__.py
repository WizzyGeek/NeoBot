from discord import Intents
from NeoBot import Neo, Config

def get_intents() -> Intents:
    intents = Intents.all()
    intents.typing = False
    return intents

if __name__ == "__main__":
    ConfigObj: Config = Config()
    NeoBot: Neo = Neo(ConfigObj, description="**Assassination\'s discord bot**\ndeveloped by TEEN_BOOM [here!](https://github.com/TEEN-BOOM/NeoBot) with discord.py", intents=get_intents())
    NeoBot.run()
