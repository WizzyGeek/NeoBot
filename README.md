# ![NeoBot](https://user-images.githubusercontent.com/51919967/86535024-01884d00-befb-11ea-8e27-577e6344413b.png)
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2FTEEN-BOOM%2FNeoBot.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2FTEEN-BOOM%2FNeoBot?ref=badge_shield)

# ⦗![Open Source](https://opensource.org/files/osi_favicon.png)⦘Neo a discord bot

Simple, Modular and Multifuctional

[![Python](https://forthebadge.com/images/badges/made-with-python.svg)](https://www.python.org/)<br>
[![:o](https://forthebadge.com/images/badges/you-didnt-ask-for-this.svg)](https://secureimg.stitcher.com/feedimagesplain328/158438.jpg)<br>
[![No Gluten](https://forthebadge.com/images/badges/gluten-free.svg)](https://image.shutterstock.com/image-vector/gluten-free-icon-vector-round-260nw-778351531.jpg)<br>
[![Warranty](https://img.shields.io/badge/NO-WARRANTY!-ff0000?style=for-the-badge&logo=appveyor&labelColor=cc0000)]()<br>
[![Discord](https://img.shields.io/discord/583689248117489675?logo=DISCORD&style=for-the-badge)](https://discord.gg/YgnxxEC)<br>
![GitHub repo size](https://img.shields.io/github/repo-size/TEEN-BOOM/NeoBot?style=for-the-badge)<br>
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/TEEN-BOOM/NeoBot.git)

## Using this repo's Cogs

Except `Prefix.py`, `Sudo.py`, `moderation.py` most cogs can be used in other discord.py bots without much changes.
If you wish to use packaged cog as a single file (eg: Connect4), then look for a folder called `SC` in the cog which 
contains a ".pysc" file, this file can be used as a cog after changing the suffix to ".py"
Do not use files from `NeoBot.SC` since these are in development or they are obsolete or simply not in use,
they are kept in the repo for further future development.

## Hosting 

### Requirements
 - `requirements.txt` | All recommended dependencies with timber and uvloop | `python3 -m pip install -r requirements.txt`
 - `hard-requirements.txt` | Minimum required dependencies | `python3 -m pip install -r hard-requirements.txt`<br>
`lavalink.json` or use [music-legacy.pysc](https://github.com/TEEN-BOOM/NeoBot/blob/master/NeoBot/cogs/SC/music-legacy.pysc)<br>
`secret.json` or set enviroment variables<br>
`timber.json` - optional

#### secret.json
self-hosting requires you to create a file named `secret.json`
with the following structure 
```json
{
    "credentials":{
        "token": "<token>",
        "DATABASE_URL": "URL",
        "wavepass": "pass"
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
#### lavalink.json
For music functionality edit the file named `lavalink.json` if you have setup a [Lavalink server](https://github.com/Frederikam/Lavalink/releases/) with the following structure:
```json
{
    "MAIN": {
        "host": "lavaserver.host.com",
        "port": 80,
        "rest_uri": "http://lavaserver.host.com",
        "identifier": "MAIN",
        "region": "europe",
        "heartbeat": 40.0
        }
}
```
heartbeat is required if your vps closes idle connections.
#### music-legacy
If you wish to not use Lavalink then remane `music.pysc` -> `music.py` & delete `Music.py`, uninstall wavelink `python3 -m pip uninstall wavelink`
and download FFmpeg binary for your platform and install opuslib if you do not use discord.py on windows
##### music-legacy for heroku
Add the build packs, after following above steps.
- https://github.com/xrisk/heroku-opus.git
- https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git

### Credentials : method 1
Requires `secret.json`

### method 2 

Set enviroment variables, this is done during setup for heroku.
Also you will need to ~~change `config` dict at line 60 in bot.py (Will be moved to database in future)~~ configuure the bot for the server using `config` command.

### method 3 (Not reccomended with hardcoding)
Creating a config object with similar attributes
example:
```py
from NeoBot.Utils import Config, 

Class Credentials(Config):
    def __init__(self):
        self.token = "tokenhardcodedorloaded"
        self.dburl = "url"
        self.rid = "redditid"
        self.rsecret = "reddit_secret"
        # self.config to be removed in future to set it from commands
        self.config = {
            "welchannel": 23456789,
            "log": 23876556789
        }
        # to move to asyncpg for leveling system
        self.cur = psycopg2.connect(self.dburl)
        self.conn = self.conn.cursor()

if __name__ == '__main__':
    ConfigObj = Credentials()
    Neo = Neo(ConfigObj)
    Neo.run()
    ConfigObj2 = Config()
    SomeOtherBot = Neo(ConfigObj2) # You can run multiple bots using different bot and config objects
    SomeotherBot.run()
```
### method 4
Directly set attributes in Bot Class.

#### For heroku 
you need to set the value for config variables, token and reddit (reccomended) or use a `secret.json` file.
The buildpacks and addons will be added automatically.

## Contribution
You are welcome to contribute to the bot!

## TODO
- [ ] Fix all code (90%)
- [ ] Rewrite the bot (60%)
- [ ] Use asyncpg (70%)
- [ ] Remove psycopg2 (10%)

## License
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2FTEEN-BOOM%2FNeoBot.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2FTEEN-BOOM%2FNeoBot?ref=badge_large)