from NeoBot import Neo, Config

if __name__ == "__main__":
    ConfigObj: Config = Config()
    NeoBot: Neo = Neo(ConfigObj, description="**Assassination\'s discord bot**\ndeveloped by TEEN_BOOM [here!](https://github.com/TEEN-BOOM/NeoBot) with discord.py")
    NeoBot.run()
