import requests
import logging
import os
import yaml
import sys
from abc import ABC, abstractmethod
from google.cloud import translate_v2 as translate
from google.oauth2 import service_account
from enum import Enum

logger = logging.getLogger(f"{os.path.basename(os.path.dirname(__file__))}.{__name__}")
logger.addHandler(logging.StreamHandler(sys.stdout))


class TranslatorEnum(Enum):
    """
    Enum to store allowed values for translators
    """
    GOOGLE: str = 'google'
    YANDEX: str = 'yandex'


class BaseTranslator(ABC):
    @abstractmethod
    def translate(self, text: str, source_language: str, target_language: str) -> dict:
        """
        Translate provided text
        :param target_language: Target language code
        :param source_language: Source language code
        :param text: Text to be translated
        :return: Dictionary in form {"input": str, "input_language": str, "output": list, "output_language": str}
        """
        pass


class YandexTranslator(BaseTranslator):
    """
    Class to translate text using Yandex Translate Service.
    """
    def __init__(self, api_key: str, api_url: str):
        """
        :param api_key: API Key
        """
        self.api_key = api_key
        self.api_url = api_url
        self.body = {
            "sourceLanguageCode": "en",
            "format": "PLAIN_TEXT",
            "targetLanguageCode": "ru",
            "texts": [],
            "speller": True
        }
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {self.api_key}"
        }

    def translate(self, text: str, source_language: str = 'en', target_language: str = "ru") -> dict:
        """
        Translate provided text
        :param target_language: Target language code
        :param source_language: Source language code
        :param text: Text to be translated
        :return: Dictionary in form {"input": str, "input_language": str, "output": list, "output_language": str}
        """
        self.body["texts"] = [text]
        self.body["sourceLanguageCode"] = source_language
        self.body["targetLanguageCode"] = target_language
        result = {
            "input": text,
            "input_language": source_language,
            "output": [],
            "output_language": target_language
        }
        try:
            response = requests.post(
                self.api_url,
                json=self.body,
                headers=self.headers
            )
            if response.status_code == 200:
                result["output"].extend([item["text"] for item in response.json()["translations"]])
            else:
                logger.error(f"Response from Yandex service: "
                             f"{{\"response_code\": {response.status_code}, \"response_body\": {response.text}}}")
        except Exception as e:
            logger.error(f"Error while requesting Yandex service: {e}")

        return result


class GoogleTranslator(BaseTranslator):
    """
    Class to translate text using Google service
    """
    def __init__(self, creds_file_path: str):
        """
        :param creds_file_path: Google credentials file path
        """
        self.creds = service_account.Credentials.from_service_account_file(creds_file_path)
        self.translate_client = translate.Client(credentials=self.creds)

    def translate(self, text: str, source_language: str = "en", target_language: str = "ru") -> dict:
        """
        Translate provided text
        :param target_language: Target language code
        :param source_language: Source language code
        :param text: Text to be translated
        :return: Dictionary in form {"input": str, "input_language": str, "output": list, "output_language": str}
        """
        result = {
            "input": text,
            "input_language": source_language,
            "output": [],
            "output_language": target_language
        }
        try:
            response = self.translate_client.translate(
                values=text,
                source_language=source_language,
                target_language=target_language
            )
            result["output"].extend([response['translatedText']])
        except Exception as e:
            logger.error(f"Error while requesting Google service: {e}")

        return result


class Translator:
    """
    Encapsulates translation logic regardless of used translation service
    """
    def __init__(self, translator: TranslatorEnum):
        self.translator = self._get_translator(translator)

    def _get_translator(self, translator: TranslatorEnum) -> BaseTranslator:
        """
        Creates and configures Translator
        :param translator: Translator service to be used
        :return:
        """
        if translator.value == "google":
            return GoogleTranslator(creds_file_path=os.path.join("config", "google.json"))
        elif translator.value == "yandex":
            with open(os.path.join("config", "svc.yaml"), "r") as file:
                config = yaml.safe_load(file)
            return YandexTranslator(
                api_key=config['yandex']["api_key"],
                api_url=config['yandex']["api_base_url"]
            )
        else:
            raise NotImplementedError

    def translate(self, text: str):
        """
        Translate provided text
        :param text: Text to be translated
        :return: Dictionary in form {"input": str, "input_language": str, "output": list, "output_language": str}
        """
        return self.translator.translate(text)
