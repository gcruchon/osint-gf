from includes import telegram, log, mongo

log.info("------------ NEW RUN ------------")



EXCLUDED_CHANNEL_URLS = ["https://t.me/AmplifyUkraine"]
ADDITIONNAL_CHANNEL_URLS = ["https://t.me/UkraineNow"]
SKIP_MY_CHANNELS = True
SKIP_ADDITIONNAL_CHANNELS = False

mongo_telegram = mongo.MongoTelegram()
tg = telegram.Telegram(mongo_telegram)
tg.set_excluded_channels(EXCLUDED_CHANNEL_URLS)


async def main():
    # Getting information about yourself
    me = await tg.get_client().get_me()

    # "me" is a user object. You can pretty-print
    # any Telegram object with the "stringify" method:
    log.info(me.stringify())

    if not SKIP_MY_CHANNELS:
        async for dialog in tg.get_client().iter_dialogs():
            if dialog.is_channel or dialog.name == "Telehunt":
                await tg.save_channel(dialog.entity)

    if not SKIP_ADDITIONNAL_CHANNELS:
        for channel_url in ADDITIONNAL_CHANNEL_URLS:
            channel_entity = await tg.get_client().get_entity(channel_url)
            if channel_entity:
                await tg.save_channel(channel_entity)


with tg.get_client():
    tg.get_client().loop.run_until_complete(main())
