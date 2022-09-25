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
        message["created"] = datetime.utcnow()
        message_id = self._messages.insert_one(message).inserted_id
        log.info("Messages inserted: {}".format(message_id))

    def get_messages_without_lang(self):
        log.info("Get messages without lang")
        messages = self._messages.find(
            filter={"lang": {"$exists": False}},
            projection={"_id": True, "raw_text": True, "web_preview": True},
        )
        return messages

    def add_lang_to_message(self, message_id, lang, web_preview = None):
        message_filter = {"_id": message_id}
        lang_values = {"$set": {"lang": lang, "lang_detected": datetime.utcnow()}}
        if web_preview != None:
            lang_values["$set"]["web_preview"] = web_preview
        result = self._messages.update_one(message_filter, lang_values)
        if result.modified_count != 1:
            raise MongoTelegramException(
                "Error when trying to update language of the following message ({})".format(
                    message_id
                )
            )
        log.info(
            "Lang added to message ({}): {}".format(message_id, result.modified_count)
        )


class MongoTelegramException(Exception):
    """Exception class for MongoTelegram"""

    pass
