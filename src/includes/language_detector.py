import fasttext
from os import path
from includes import log

MODEL_DIR = path.join(path.dirname(path.realpath(__file__)), "..", "models")
LIGHT_MODEL = path.join(MODEL_DIR, "lid.176.ftz")
HEAVY_MODEL = path.join(MODEL_DIR, "lid.176.bin")
CONFIDENCE_THRESHOLD = 0.9
LANG_UNDEFINED = "Undefined"


class LanguageDetector:
    def __init__(self):
        pretrained_lang_model = LIGHT_MODEL
        log.debug("Model used: {}".format(pretrained_lang_model))
        self._model = fasttext.load_model(pretrained_lang_model)
        log.info("Model loaded.")

    def _clean_text(self, text):
        return text.replace("\n", "")

    def _predict_lang(self, text):
        predictions = self._model.predict(self._clean_text(text), k=3)
        return predictions

    def _get_languages(self, text):
        languages, confidence_rates = self._predict_lang(text)
        detected_languages = []
        for lang in languages:
            confidence = confidence_rates[languages.index(lang)]
            if confidence >= CONFIDENCE_THRESHOLD:
                detected_languages.append(lang)
        return detected_languages

    def get_language(self, text):
        languages = self._get_languages(text)
        if len(languages) == 0:
            return LANG_UNDEFINED
        else:
            return languages[0].replace("__label__", "")
