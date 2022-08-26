from os import environ
from telethon import TelegramClient
from includes import log, helpers
from asyncstdlib import builtins
from os import path, environ, makedirs
from datetime import date, timedelta

TG_API_ID = environ["TG_API_ID"]
TG_API_HASH = environ["TG_API_HASH"]

EXPORT_BASE_FOLDER = "export"
NUMBER_OF_DAYS_TO_RETRIEVE = 1
SKIP_SAVING_VIDEOS = True


class Telegram:
    def __init__(self):
        self.__client = TelegramClient("anon", TG_API_ID, TG_API_HASH)
        self.__excluded_channels = None
        self.__excluded_ids = None
        log.info("Telegram Client Created")

    def set_excluded_channels(self, excluded_channels):
        self.__excluded_channels = excluded_channels

    def get_client(self):
        return self.__client

    async def __get_channel_id(self, url):
        channel = await self.__client.get_entity(url)
        return channel.id

    async def __is_excluded(self, channel_id):
        if self.__excluded_channels == None:
            raise TelegramException("Excluded channels non initialized")
        if self.__excluded_ids == None:
            self.__excluded_ids = await builtins.list(
                builtins.map(self.__get_channel_id, self.__excluded_channels)
            )
        return channel_id in self.__excluded_channels

    def __get_message_channel_id(self, message):
        if hasattr(message, "peer_id") and hasattr(message.peer_id, "channel_id"):
            return message.peer_id.channel_id
        else:
            return message.chat_id

    def __get_message_iso_date(self, message):
        return message.date.strftime("%Y-%m-%d")

    def __get_message_root_dir(self, message):
        message_dir = path.join(
            EXPORT_BASE_FOLDER,
            "{}".format(self.__get_message_channel_id(message)),
            self.__get_message_iso_date(message),
        )
        makedirs(message_dir, exist_ok=True)
        return message_dir

    def __get_message_path(self, message):
        return path.join(self.__get_message_root_dir(message), "{}".format(message.id))

    def __get_album_path(self, message):
        return path.join(
            self.__get_message_root_dir(message), "album-{}".format(message.grouped_id)
        )

    async def __save_media(self, message, is_album=False):

        if message.photo or message.file:
            if is_album:
                base_dir = self.__get_album_path(message)
            else:
                base_dir = self.__get_message_path(message)

            if message.file.name:
                file_name = path.join(
                    base_dir,
                    helpers.clean_string(message.file.name),
                )
            else:
                file_name = path.join(base_dir, "photo-{}".format(message.id))

            if message.photo or not SKIP_SAVING_VIDEOS:
                file_path = await message.download_media(file_name)
                log.info(
                    "\tFile saved to {}".format(file_path)
                )  # printed after download is done

    async def __save_message(self, message):
        log.info(
            "channel({}) - save_message({})".format(
                self.__get_message_channel_id(message), message.id
            )
        )
        file = open(
            "{}.txt".format(self.__get_message_path(message)), "w", encoding="utf-8"
        )
        file.write("Channel ID ={}\n\n".format(self.__get_message_channel_id(message)))
        for att in dir(message):
            if not att.startswith("_") and not helpers.has_method(message, att):
                file.write("{}={}\n\n".format(att, getattr(message, att)))
        file.close()

        await self.__save_media(message)

    def __add_to_albums(self, message, albums):
        grouped_id = message.grouped_id
        log.info(
            "channel({}) - add_to_albums[{}] message({}))".format(
                self.__get_message_channel_id(message), grouped_id, message.id
            )
        )
        if grouped_id in albums:
            albums[grouped_id].append(message)
        else:
            albums[grouped_id] = [message]

    async def __save_albums(self, albums):
        log.info("Saving albums")
        for grouped_id in albums:
            log.info("Grouped Id: {}".format(grouped_id))
            await self.__save_album(albums[grouped_id])

    async def __save_album(self, messages):
        log.info("Saving album - {} messages".format(len(messages)))
        for idx, message in enumerate(messages):
            log.info("\tMessage #{}".format(idx))
            if idx == 0:
                file = open(
                    "{}.txt".format(self.__get_album_path(message)), "w", encoding="utf-8"
                )
                file.write(
                    "Channel ID ={}\n\n".format(self.__get_message_channel_id(message))
                )
                for att in dir(message):
                    if not att.startswith("_") and not helpers.has_method(message, att):
                        file.write("{}={}\n\n".format(att, getattr(message, att)))
                file.close()

            await self.__save_media(message, is_album=True)

    async def save_channel(self, channel_entity):
        title = channel_entity.title
        channel_id = channel_entity.id

        log.info("Saving channel ({}): {}".format(channel_id, title))
        if await self.__is_excluded(channel_id):
            log.info("{} is excluded -- skipped".format(title))
        else:
            albums = {}
            offset_date = date.today() - timedelta(days=(NUMBER_OF_DAYS_TO_RETRIEVE-1))
            async for message in self.__client.iter_messages(
                channel_entity, offset_date=offset_date, reverse=True
            ):
                if message.grouped_id:
                    log.debug(
                        "For channel({}), grouped_id found {}".format(
                            title, message.grouped_id
                        )
                    )
                    self.__add_to_albums(message, albums)
                else:
                    await self.__save_message(message)

            await self.__save_albums(albums)


class TelegramException(Exception):
    """Exception class for the project"""

    pass
