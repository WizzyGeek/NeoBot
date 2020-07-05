from NeoBot import Neo, Config

if __name__ == "__main__":
    ConfigObj: Config = Config()
    NeoBot: Neo = Neo(ConfigObj)
    NeoBot.run()
