from includes import telegram, log, mongo, s3

log.info("------------ NEW RUN ------------")


EXCLUDED_CHANNEL_URLS = ["https://t.me/AmplifyUkraine"]
ADDITIONNAL_CHANNEL_URLS = ["https://t.me/UkraineNow"]
SKIP_MY_CHANNELS = False
SKIP_ADDITIONNAL_CHANNELS = False

mongo_telegram = mongo.MongoTelegram()
s3_storage = s3.AwsStorage()

tg = telegram.Telegram(db=mongo_telegram, file_storage=s3_storage)
tg.set_excluded_channels(EXCLUDED_CHANNEL_URLS)


async def main():
    # Getting information about yourself
    me = await tg.get_client().get_me()

    # "me" is a user object. You can pretty-print
    # any Telegram object with the "stringify" method:
    log.info(me.stringify())
    nb_messages = 0

    if not SKIP_MY_CHANNELS:
        async for dialog in tg.get_client().iter_dialogs():
            if dialog.is_channel or dialog.name == "Telehunt":
                nb_messages += await tg.save_channel(dialog.entity)

    if not SKIP_ADDITIONNAL_CHANNELS:
        for channel_url in ADDITIONNAL_CHANNEL_URLS:
            channel_entity = await tg.get_client().get_entity(channel_url)
            if channel_entity:
                nb_messages += await tg.save_channel(channel_entity)

    msg = "Number of messages imported: {}".format(nb_messages)
    log.info(msg)
    print(msg)


with tg.get_client():
    tg.get_client().loop.run_until_complete(main())
