from pymongo import MongoClient
from os import environ
from urllib import parse
from datetime import datetime
from includes import log


class MongoTelegram:
    def __init__(self):
        username = parse.quote_plus(environ["MONGODB_USERNAME"])
        password = parse.quote_plus(environ["MONGODB_PASSWORD"])

        self._client = MongoClient(
            "mongodb://{}:{}@localhost:27017/telegram".format(username, password)
        )
        self._db = self._client["telegram"]
        self._messages = self._db.messages
        log.info("Mongo Client Created")

    def insert_message(self, message):
        message['created'] = datetime.utcnow()
        message_id = self._messages.insert_one(message).inserted_id
        log.info("Messages inserted: {}".format(message_id))
