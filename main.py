from KorosenseiBot import Bot, Config

if __name__ == "__main__":
    ConfigObj: Config = Config()
    korosensei: Bot = Bot(ConfigObj)
    korosensei.run()
