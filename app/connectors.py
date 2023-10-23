"""
Classes to work with external services
"""
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from models import WordResponse
import requests
import json


@dataclass
class ConnectorConfig:
    """
    Class for storing configuration for particular service.
    """
    base_url: str
    api_key: str = field(default=None)


class BaseConnector(ABC):
    """
    Abstract class for all connectors
    """
    @abstractmethod
    def __init__(self, config: ConnectorConfig):
        pass

    @abstractmethod
    def request(self, word: str):
        pass


class MWThesaurusConnector(BaseConnector):
    """
    Class for Merriam-Webster Thesaurus service
    """
    def __init__(self, config: ConnectorConfig):
        self.base_url = config.base_url
        self.api_key = config.api_key

    def request(self, word_id: str):
        try:
            response = requests.get(url=f"{self.base_url}/{word_id}", params={"key": self.api_key})
            response_json = response.json()
            word_item = WordResponse(
                word=word_id,
                definitions=response_json[0]["shortdef"],
                translations={},
                synonyms=response_json[0]["meta"]["syns"][0],
                examples=[response_json[0]["def"][0]["sseq"][0][0][1]["dt"][1][1][0]["t"]]
            )
        except Exception as ex:
            logging.error(f"Unable to request external service: {ex}")
            raise RuntimeError
        return word_item
