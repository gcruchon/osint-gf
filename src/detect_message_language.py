from includes import log, mongo, language_detector

log.info("------------ DETECT MESSAGE LANGUAGE ------------")


mongo_telegram = mongo.MongoTelegram()
detector = language_detector.LanguageDetector()

def get_lang_in_web_preview(web_preview):
    web_preview_with_lang = web_preview.copy()

    if "title" in web_preview and web_preview["title"] != None:
        web_preview_with_lang['lang_title'] = detector.get_language(web_preview["title"])
    if "description" in web_preview and web_preview["description"] != None:
        web_preview_with_lang['lang_description'] = detector.get_language(web_preview["description"])
    
    return web_preview_with_lang

def main():
    # Getting information about yourself
    messages = mongo_telegram.get_messages_without_lang()
    nb_detected = 0
    for message in messages:
        web_preview = None
        if 'web_preview' in message:
            web_preview = get_lang_in_web_preview(message['web_preview'])

        detected_language = detector.get_language(message["raw_text"])
        mongo_telegram.add_lang_to_message(message["_id"], detected_language, web_preview)
        nb_detected += 1

    msg = "Number of language detections in messages: {}".format(nb_detected)
    log.info(msg)
    print(msg)


if __name__ == "__main__":
    main()
