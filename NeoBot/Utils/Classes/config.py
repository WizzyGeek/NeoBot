import json
import logging
import os
import sys
from typing import Dict, Union, Optional
import psycopg2

import asyncpg

logger: logging.Logger = logging.getLogger(__name__)


class Config: # REASON: [Make it accessible on hover in ide.]
    """Collect all the required info.
        
            Requires a `secret.json` or envirment variables 
            and `lavalink.json` (optional) in the root directory.

        Args:
            MusicState (bool, optional):  Set the MusicState to false if Lavalink server is not available. Defaults to True.
    """
    
    def __init__(self, MusicState: bool = True):
        """Collect all the required info.
        
            Requires a `secret.json` or envirment variables 
            and `lavalink.json` (optional) in the root directory.

        Args:
            MusicState (bool, optional):  Set the MusicState to false if Lavalink server is not available. Defaults to True.
        """
        self.MusicState: bool = MusicState
        try:
            self.token: str = str(os.environ["token"])  # Redunant but gives me peace of mind.
            self.dburl: str = str(os.environ["DATABASE_URL"])
            self.rid: str = str(os.environ["reddit_id"])
            self.rsecret: str = str(os.environ["reddit_secret"])
            self.config: Dict[str, int] = {
                "welchannel": 583703372725747713,
                "log": 709339678863786084
            }
            self.wavepass = str(os.environ["wavepass"])
        except KeyError as key:
            logger.warning(
                "Enviroment Variables don\'t contain credentials (specifically - %s), seeking secret.json", key.args[0])
            try:
                # This is the CWD.
                with open("secret.json", "r") as reader:
                    self.data = json.loads(reader.read())
            except FileNotFoundError:
                logger.error(
                    "secret.json not found | More Info here https://github.com/TEEN-BOOM/korosensei/blob/master/README.md")
                # Sorry python lords, I couldn"t do it gracefully without this.
                sys.exit()
            except Exception:
                logger.exception("An unexpected error occured")
                sys.exit()
            else:
                try:
                    _creds: Dict[str, str] = self.data["credentials"]
                    self.token: str = _creds["token"]
                    self.dburl: str = _creds["DATABASE_URL"]
                    self.wavepass: str = _creds["wavepass"]
                    _reddit: Dict[str, str] = self.data["reddit"]
                    self.rid: str = _reddit["id"]
                    self.rsecret: str = _reddit["secret"]
                    self.config: Dict[str, int] = self.data["config"]  # TODO:: [REMOVE THIS]
                except KeyError as err:
                    logger.exception(
                        f"{err.args[0]} not found, secret.json not structured properly | More Info here https://github.com/TEEN-BOOM/korosensei/blob/master/README.md")
                    sys.exit()
                except Exception:
                    logger.exception("An unexpected error occured")
                else:
                    logger.info("Credentials initialised")
        else:
            logger.info("Credentials initialised")
        #----------------------------------------#
        logger.info("Config Object initialised")

    async def __ainit__(self, MaxPoolSize: int = 5):
        self.pool: asyncpg.pool.Pool = await asyncpg.create_pool(dsn=self.dburl,  min_size=1, max_size=MaxPoolSize)

    @property
    def linkcreds(self) -> Optional[Union[dict, Exception]]:
        """Fetch the lavalink credentials.
        
            A `lavalink.json` file is required in the root directory.
            

        Returns:
            Union[dict, Exception, None]: 
                Return None if MusicState is None, return error if an unexpected error occurs and return the dict if no errors were caught
        """        
        if self.MusicState:
            try:
                # This is the CWD.
                with open("lavalink.json", "r") as reader:
                    return json.loads(reader.read())
            except FileNotFoundError:
                logger.warning(
                    "lavalink.json not found continuing without music extension | More Info here https://github.com/TEEN-BOOM/korosensei/blob/master/README.md")
            except Exception as err:
                logger.exception("An unexpected error occured")
                return err
        else:
            return None

    def DB(self) -> bool:
        """Initialize the DB connection"""
        try:
            self.conn = psycopg2.connect(self.dburl)
        except NameError:
            logger.exception("Unexpected error occured!")
            return False
        except Exception:
            logger.exception("Cannot connect to postgre database")
            return False
        self.cur = self.conn.cursor()
        self.table_query()
        return True
        # logger.debug(f"Initialised config variables : {self.__dict__}") # Dangerous enable in secure condition only
    
    def table_query(self):
        try:
            self.cur.execute(
                "CREATE TABLE IF NOT EXISTS prefix(gid BIGINT NOT NULL UNIQUE, prefix TEXT NOT NULL)")
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS
                    server(
                        gid BIGINT NOT NULL UNIQUE,
                        modlog BIGINT UNIQUE,
                        welchannel BIGINT UNIQUE)""")
            self.conn.commit()
        except:
            logger.exception("Database error occured!")
