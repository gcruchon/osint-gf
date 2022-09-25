import translators as ts

PROVIDER_GOOGLE = "google"
PROVIDER_BING = "bing"
PROVIDER_DEEPL = "deepl"
DEFAULT_PROVIDER = PROVIDER_GOOGLE
DESTINATION_LANGUAGE = "en"


class TextTranslator:
    def __init__(
        self, provider=DEFAULT_PROVIDER, destination_language=DESTINATION_LANGUAGE
    ):
        self._provider = provider
        self._destination_language = destination_language

    def _translate(self, text):
        translated_text = None
        if self._provider == PROVIDER_GOOGLE:
            translated_text = ts.google(
                text, if_use_cn_host=False, to_language=self._destination_language
            )
        if self._provider == PROVIDER_BING:
            translated_text = ts.bing(
                text, if_use_cn_host=False, to_language=self._destination_language
            )
        if self._provider == PROVIDER_DEEPL:
            translated_text = ts.deepl(text, to_language=self._destination_language)
        return translated_text

    def _is_url(self, text):
        return (
            text.startswith("https://")
            or text.startswith("http://")
            or text.startswith("ftp://")
            or text.startswith("ftps://")
        )

    def _do_not_translate(self, text):
        return self._is_url(text)

    def translate(self, text):
        if self._do_not_translate(text):
            return text
        else:
            return self._translate(text)
