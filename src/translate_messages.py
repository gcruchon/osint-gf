from includes import log, mongo, translator
from concurrent.futures import ThreadPoolExecutor, as_completed

log.info("------------ TRANSLATE MESSAGE ------------")


mongo_telegram = mongo.MongoTelegram()
text_translator = translator.TextTranslator()


def translate_web_preview(web_preview):
    translated_web_preview = web_preview.copy()

    if (
        "lang_title" in web_preview
        and web_preview["lang_title"] != translator.DESTINATION_LANGUAGE
    ):
        log.info("Original title={}".format(web_preview["title"]))
        translated_web_preview["translated_title"] = text_translator.translate(
            web_preview["title"]
        )
        log.info(
            "Translated title={}".format(translated_web_preview["translated_title"])
        )
    if (
        "lang_description" in web_preview
        and web_preview["lang_description"] != translator.DESTINATION_LANGUAGE
    ):
        log.info("Original description={}".format(web_preview["description"]))
        translated_web_preview["translated_description"] = text_translator.translate(
            web_preview["description"]
        )
        log.info(
            "Translated description={}".format(
                translated_web_preview["translated_description"]
            )
        )

    return translated_web_preview


def translate_message(message):
    web_preview = None
    translation = None
    if "web_preview" in message:
        web_preview = translate_web_preview(message["web_preview"])

    if "lang" in message and message["lang"] != translator.DESTINATION_LANGUAGE:
        log.info("Original raw_text={}".format(message["raw_text"]))
        translation = text_translator.translate(message["raw_text"])
        log.info("Translated raw_text={}".format(translation))

    return message["_id"], translation, web_preview


def main():
    # Getting information about yourself
    messages = mongo_telegram.get_messages_to_be_translated("en")
    nb_translated = 0

    with ThreadPoolExecutor() as executor:
        future_res = {
            executor.submit(translate_message, message): "{}".format(message["_id"])
            for message in messages
        }
        for future in as_completed(future_res):
            m_id = future_res[future]
            try:
                message_id, translation, web_preview = future.result()
            except Exception as exc:
                log.error(m_id)
                log.error(exc)
                print("Exception for ({}): {}".format(m_id, exc))
            else:
                mongo_telegram.add_translation_to_message(
                    message_id, translation, web_preview
                )
                nb_translated += 1

    msg = "Number of translation in messages: {}".format(nb_translated)
    log.info(msg)
    print(msg)


if __name__ == "__main__":
    main()
