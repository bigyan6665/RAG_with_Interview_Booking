import redis
import json
from dotenv import load_dotenv
import os

load_dotenv() # Loads variables from .env into os.environ

class ChatMemory:
    def __init__(self, sessionid:str):
        """
        Description:
            Constructor to initialize the chat memory
        """
        self.REDIS_DB_USERNAME = os.getenv("REDIS_DB_USERNAME") # access variables
        self.REDIS_DB_PASSWORD = os.getenv("REDIS_DB_PASSWORD") # access variables
        self.SESSION_TTL_SECONDS = 500 # in seconds
        self.redis_client = self.create_connection()
        self.SESSIONID = sessionid

    def create_connection(self) -> redis.Redis:
        """"
        Description:
            Method to create connection with redis 
        Return:
            Redis client object
        """
        try:
            redis_client = redis.Redis(
                host='redis-12530.c257.us-east-1-3.ec2.cloud.redislabs.com',
                port=12530,
                decode_responses=True,
                username=self.REDIS_DB_USERNAME,
                password=self.REDIS_DB_PASSWORD,)
            return redis_client
        except Exception as e:
            raise Exception(f"Error in creating connection with redis: {e}")

    def get_chat_history(self) -> list:
        """
        Docstring for get_chat_history
        Return:
            list of chat histories
        """
        key = f"chat:{self.SESSIONID}"
        data = self.redis_client.lrange(key,0,-1)
        self.redis_client.expire(key, self.SESSION_TTL_SECONDS) # sets/refreshes time to live period of the specified key
        return data if data else []

    def save_chat_history(self,history: dict) -> None:
        """
        Docstring for save_chat_history

        Arguments:
            history: history to save

        """
        key = f"chat:{self.SESSIONID}"
        self.redis_client.rpush(key, json.dumps(history)) # pushes the additional history at the end of the list
        self.redis_client.expire(key, self.SESSION_TTL_SECONDS) # sets/refreshes time to live period of the specified key
