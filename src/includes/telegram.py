from os import environ
from telethon import TelegramClient, utils
from includes import log, helpers
from asyncstdlib import builtins
from os import path, environ, makedirs
from datetime import date, timedelta

TG_API_ID = environ["TG_API_ID"]
TG_API_HASH = "{}".format(environ["TG_API_HASH"])

EXPORT_BASE_FOLDER = "export"
NUMBER_OF_DAYS_TO_RETRIEVE = 1
SKIP_SAVING_VIDEOS = True


class Telegram:
    def __init__(self, db=None, file_storage=None):
        self._db = db
        self._file_storage = file_storage
        self._client = TelegramClient("anon", TG_API_ID, TG_API_HASH)
        self._excluded_channels = None
        self._excluded_ids = None
        if self._db == None:
            raise TelegramException("No db selected")
        if self._file_storage == None:
            raise TelegramException("No file storage selected")
        log.info("Telegram Client Created")

    def set_excluded_channels(self, excluded_channels):
        self._excluded_channels = excluded_channels

    def get_client(self):
        return self._client

    async def _get_channel_id(self, url):
        channel = await self._client.get_entity(url)
        return channel.id

    async def _is_excluded(self, channel_id):
        if self._excluded_channels == None:
            raise TelegramException("Excluded channels non initialized")
        if self._excluded_ids == None:
            self._excluded_ids = await builtins.list(
                builtins.map(self._get_channel_id, self._excluded_channels)
            )
        return channel_id in self._excluded_channels

    def _get_message_channel_id(self, message):
        if hasattr(message, "peer_id") and hasattr(message.peer_id, "channel_id"):
            return message.peer_id.channel_id
        else:
            return message.chat_id

    def _get_message_iso_date(self, message):
        return message.date.strftime("%Y-%m-%d")

    def _get_message_root_dir(self, message):
        message_dir = path.join(
            EXPORT_BASE_FOLDER,
            "{}".format(self._get_message_channel_id(message)),
            self._get_message_iso_date(message),
        )
        makedirs(message_dir, exist_ok=True)
        return message_dir

    def _get_message_path(self, message):
        return path.join(self._get_message_root_dir(message), "{}".format(message.id))

    def _get_album_path(self, message):
        return path.join(
            self._get_message_root_dir(message), "album-{}".format(message.grouped_id)
        )

    async def _save_media(self, message, is_album=False):

        media_path = None

        if message.photo or message.file:
            if is_album:
                base_dir = self._get_album_path(message)
            else:
                base_dir = self._get_message_path(message)

            if message.file.name:
                file_name = path.join(
                    base_dir,
                    helpers.clean_string(message.file.name),
                )
            else:
                file_name = path.join(base_dir, "photo-{}".format(message.id))

            ext = utils.get_extension(message.media)
            file_name = "{}{}".format(file_name, ext)

            if message.photo or not SKIP_SAVING_VIDEOS:
                data = await self._client.download_media(message, file=bytes)
                media_path = self._file_storage.store_file(
                    file_path=file_name, data=data
                )
                log.info("\tFile saved to {}".format(file_name))

        return media_path

    def _message_has_web_preview(self, message):
        return (
            hasattr(message, "web_preview") and getattr(message, "web_preview") != None
        )

    def _get_web_preview_dict(self, web_preview):
        web_preview_dict = {}
        web_preview_dict["url"] = getattr(web_preview, "url")
        web_preview_dict["site_name"] = getattr(web_preview, "site_name")
        web_preview_dict["title"] = getattr(web_preview, "title")
        web_preview_dict["description"] = getattr(web_preview, "description")
        return web_preview_dict

    def _get_message_dict(self, channel_id, message):
        message_dict = {}
        message_dict["channel_id"] = channel_id
        message_dict["chat_id"] = getattr(message, "chat_id")
        message_dict["message_id"] = getattr(message, "id")
        message_dict["date"] = getattr(message, "date")
        message_dict["edit_date"] = getattr(message, "edit_date")
        message_dict["grouped_id"] = getattr(message, "grouped_id")
        message_dict["legacy"] = getattr(message, "legacy")
        message_dict["is_reply"] = getattr(message, "is_reply")
        message_dict["mentioned"] = getattr(message, "mentioned")
        message_dict["message"] = getattr(message, "message")
        message_dict["pinned"] = getattr(message, "pinned")
        message_dict["raw_text"] = getattr(message, "raw_text")
        message_dict["sender_id"] = getattr(message, "sender_id")
        message_dict["text"] = getattr(message, "text")
        message_dict["via_bot"] = getattr(message, "via_bot")
        message_dict["via_bot_id"] = getattr(message, "via_bot_id")
        message_dict["via_input_bot"] = getattr(message, "via_input_bot")
        message_dict["views"] = getattr(message, "views")
        if self._message_has_web_preview(message):
            message_dict["web_preview"] = self._get_web_preview_dict(
                getattr(message, "web_preview")
            )
        return message_dict

    async def _save_message(self, message):
        channel_id = "{}".format(self._get_message_channel_id(message))
        log.info("channel({}) - save_message({})".format(channel_id, message.id))

        media_path = None
        if not self._message_has_web_preview(message):
            media_path = await self._save_media(message)

        message_dict = self._get_message_dict(channel_id, message)
        if media_path != None:
            message_dict["media_paths"] = [media_path]

        self._db.insert_message(message_dict)

    def _add_to_albums(self, message, albums):
        grouped_id = message.grouped_id
        log.info(
            "channel({}) - add_to_albums[{}] message({}))".format(
                self._get_message_channel_id(message), grouped_id, message.id
            )
        )
        if grouped_id in albums:
            albums[grouped_id].append(message)
        else:
            albums[grouped_id] = [message]

    async def _save_albums(self, albums):
        log.info("Saving albums")
        for grouped_id in albums:
            log.info("Grouped Id: {}".format(grouped_id))
            await self._save_album(albums[grouped_id])

    async def _save_album(self, messages):
        log.info("Saving album - {} messages".format(len(messages)))
        main_message = messages[0]
        channel_id = "{}".format(self._get_message_channel_id(main_message))
        album_dict = self._get_message_dict(channel_id, main_message)
        album_dict["media_paths"] = []
        for idx, message in enumerate(messages):
            log.info("\tMessage #{}".format(idx))
            media_path = await self._save_media(message, is_album=True)
            album_dict["media_paths"].append(media_path)

        self._db.insert_message(album_dict)

    async def save_channel(self, channel_entity):
        title = channel_entity.title
        channel_id = channel_entity.id

        log.info("Saving channel ({}): {}".format(channel_id, title))
        if await self._is_excluded(channel_id):
            log.info("{} is excluded -- skipped".format(title))
        else:
            albums = {}
            offset_date = date.today() - timedelta(
                days=(NUMBER_OF_DAYS_TO_RETRIEVE - 1)
            )
            async for message in self._client.iter_messages(
                channel_entity, offset_date=offset_date, reverse=True
            ):
                if message.grouped_id:
                    log.debug(
                        "For channel({}), grouped_id found {}".format(
                            title, message.grouped_id
                        )
                    )
                    self._add_to_albums(message, albums)
                else:
                    await self._save_message(message)

            await self._save_albums(albums)


class TelegramException(Exception):
    """Exception class for the project"""

    pass
