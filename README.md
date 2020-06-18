# ⦗![Open Source](https://opensource.org/files/osi_favicon.png)⦘Korosensei a discord bot

Simple, Modular and Multifuctional

[![Python](https://forthebadge.com/images/badges/made-with-python.svg)](https://www.python.org/)<br>
[![:o](https://forthebadge.com/images/badges/you-didnt-ask-for-this.svg)](https://secureimg.stitcher.com/feedimagesplain328/158438.jpg)<br>
[![No Gluten](https://forthebadge.com/images/badges/gluten-free.svg)](https://image.shutterstock.com/image-vector/gluten-free-icon-vector-round-260nw-778351531.jpg)<br>
[![Warranty](https://img.shields.io/badge/NO-WARRANTY!-ff0000?style=for-the-badge&logo=appveyor&labelColor=cc0000)]()<br>
![Discord](https://img.shields.io/discord/583689248117489675?logo=DISCORD&style=for-the-badge)<br>
![GitHub repo size](https://img.shields.io/github/repo-size/TEEN-BOOM/korosensei?style=for-the-badge)<br>
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/TEEN-BOOM/korosensei.git)
## Hosting 

### Credentials : method 1
self-hosting rquires you to create a file named `secret.json`
with the following structure 
```json
{
    "credentials":{
        "token": "<token>",
        "DATABASE_URL": "URL"
    },
    "config": {
        "welchannel": 1234567890,
        "log": 1234567890
    },
    "reddit": {
        "id": "client_id",
        "secret": "Secret"
    }
}
```
Apart from this you will need to install all dependencies. With ffmpeg binary and libopus

### method 2 
Set enviroment variables, this is done during setup for heroku.
Also you will need to change `config` dict at line 60 in bot.py (Will be moved to database in future)
### method 3 (Not reccomended with hardcoding)
Creating a config object with similar attributes
example:
```py
Class Credentials(Config):
    def __init__(self):
        self.token = "tokenhardcodedorloaded"
        self.dburl = "url"
        self.rid = "redditid"
        self.rsecret = "reddit_secret"
        #self.config to be removed in future to set it from commands
        self.config = {
            "welchannel": 23456789,
            "log": 23876556789
        }
        #to move to asyncpg for leveling system
        self.cur = psycopg2.connect(self.dburl)
        self.conn = self.conn.cursor()

if __name__ == '__main__':
    ConfigObj = Credentials()
    korosensei = Bot(ConfigObj)
    korosensei.run()
    ConfigObj2 = Config()
    SomeOtherBot = Bot(ConfigObj2) # You can run multiple bots using different bot and config objects
    SomeotherBot.run()
```
### method 4 (Depreceated)
Directly set attributes in Bot Class. 

#### For heroku 
you need to set the value for config variables, token and reddit (reccomended) or use a `secret.json` file.
The buildpacks and addons will be added automatically.

## TODO
- [x] Fix the help command
- [ ] Switch to lavalink
- [ ] Fix all legacy code
- [ ] Fix all code
- [ ] Rewrite the bot
- [ ] Use asyncpg