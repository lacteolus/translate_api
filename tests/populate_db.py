import json
import os
import yaml
import redis
import random
import string

# Load config
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = os.getenv("REDIS_PORT", 6379)

# Set up Redis client
redis_client = redis.Redis(
    host=redis_host,
    port=redis_port,
    db=0,
    decode_responses=True,
    protocol=3
)

items = ["test", "test1", "test11", "test2", "test22", "test3", "test33"]

for item in items:
    db_item = {
        "word": item,
        "definitions": [''.join(random.choice(string.ascii_lowercase) for _ in range(5)) for _ in range(3)],
        "translations": [''.join(random.choice(string.ascii_lowercase) for _ in range(5)) for _ in range(3)],
        "synonyms": [''.join(random.choice(string.ascii_lowercase) for _ in range(7)) for _ in range(5)],
        "examples": [''.join(random.choice(string.ascii_lowercase) for _ in range(7)) for _ in range(2)],
    }

    redis_client.set(item, json.dumps(db_item))

