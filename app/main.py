from fastapi import FastAPI, HTTPException
from typing import Optional
from models import WordResponse, WordsResponse, About
from about import ABOUT
from connectors import MWThesaurusConnector, ConnectorConfig
from translators import TranslatorEnum, Translator
from itertools import islice
from config import settings
import redis
import uvicorn
import yaml
import json
import os
import logging
import sys

# Configure logger 'app.main'
logger = logging.getLogger(f"{os.path.basename(os.path.dirname(__file__))}.{__name__}")
logger.addHandler(logging.StreamHandler(sys.stdout))

# Set up Redis client
redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=0,
    decode_responses=True,
    protocol=3
)
logger.debug(f"Redis configuration: {redis_client.info()}")


# OpenAPI tags
tags = [
    {
        "name": "about",
        "description": "Technical information about API itself"
    },
    {
        "name": "main",
        "description": "Main operations"
    }
]

translator = Translator(TranslatorEnum.GOOGLE)

# Create FastAPI application
app = FastAPI(openapi_tags=tags, **ABOUT)


# Load config for Merriam-Webster service
with open(os.path.join("config", "svc.yaml"), "r") as file:
    config = yaml.safe_load(file)
mw_connector_config = ConnectorConfig(
    base_url=config["merriam-webster"]["api_base_url"],
    api_key=config["merriam-webster"]["api_key"]
)


@app.get(
    "/about",
    summary="Get general information about this API",
    description="Get general information about this API in JSON format.",
    tags=["about"]
)
def get_about(
        debug: bool = False
) -> About:
    """
    Get general information about this API
    """
    about = About(**ABOUT)
    if debug:
        about.debug = {"backend_container_id": os.getenv("HOSTNAME")}
    return about


@app.get(
    "/words",
    summary="Get all words",
    description="Get all words from DB with pagination and filtering.",
    tags=["main"]
)
def get_words(
        page_size: int = 10,
        page_num: int = 0,
        offset: int = 0,
        search: Optional[str] = "",
        translations: bool = False,
        synonyms: bool = False,
        definitions: bool = False,
        examples: bool = False
) -> WordsResponse:
    """
    Get all words from DB
    """
    response = WordsResponse(
        words=[],
        page_size=page_size,
        page_num=page_num,
        offset=offset
    )
    search_pattern = f"{search}*"
    logger.debug(f"Searching for '{search_pattern}' keys in DB.")
    items_iter = redis_client.scan_iter(search_pattern)
    start_idx = page_size * page_num
    end_idx = page_size * page_num + page_size
    for item in list(islice(items_iter, start_idx, end_idx)):
        word_item = redis_client.get(item)
        word = WordResponse(**json.loads(word_item))
        if not translations:
            word.translations = []
        if not synonyms:
            word.synonyms = []
        if not definitions:
            word.definitions = []
        if not examples:
            word.examples = []
        response.words.append(word)
    return response


@app.post(
    "/words",
    summary="Add a new word",
    description="Add a new word into DB. A new item can have custom attributes.",
    tags=["main"]
)
def post_word(request: WordResponse) -> WordResponse:
    """
    Add given word to DB
    :param request: API request body
    :return: API response as dict
    """
    logger.debug(f"Adding word '{request.word}' into DB.")
    redis_client.set(name=request.word, value=request.model_dump_json())
    return request


@app.get(
    "/words/{word}",
    summary="Get a word",
    description="Get a word from DB. If the word is not found in DB, external services are used to get information",
    tags=["main"]
)
def get_word(word: str) -> WordResponse:
    """
    Get information about given word.
    If the word is not found in local DB, information is retrieved form Google Translate service
    """
    logger.debug(f"Searching for '{word}' key in DB.")
    item = redis_client.get(word)
    if item:
        logger.debug(f"Word '{word}' was found in DB.")
        response = WordResponse(**json.loads(item))
    else:
        logger.debug(f"Word '{word}' was not found in DB. Using external services.")
        mw_connector = MWThesaurusConnector(mw_connector_config)
        # Get info from external services
        try:
            response = mw_connector.request(word_id=word)
            translation = translator.translate(word)
            response.translations = {translation["output_language"]: translation["output"]}
        except Exception as e:
            logger.error(f"Error while translating: {e}")
            raise HTTPException(status_code=404, detail="Word not found")
        # Store info into DB
        try:
            redis_client.set(name=response.word, value=response.model_dump_json())
        except Exception as e:
            logger.error(f"Error while storing data into DB: {e}")
    return response


@app.delete(
    "/words/{word}",
    summary="Delete a word",
    description="Delete a word from DB.",
    tags=["main"]
)
def delete_word(word: str) -> dict:
    """
    Delete given word from DB
    :param word: Word to be deleted
    :return: API response as dict
    """
    redis_client.delete(word)
    response_msg = f"Word '{word}' has been deleted from DB"
    logger.debug(response_msg)
    return {"detail": response_msg}


if __name__ == "__main__":
    # Run for debug purposes
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = os.getenv("REDIS_PORT", 6379)
    uvicorn.run(app, host=redis_host, port=redis_port, reload=True)
