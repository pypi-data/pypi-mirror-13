import os.path

from hashlib import sha256
from datetime import datetime

def api_time_to_datetime(value):
    if value == "":
        # CCP sends empty values for never
        return None

    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")


# A simple filesystem cache with no invalidation
def _cache_key(key):
    return "cache/{}".format(sha256(key).hexdigest())

def cache_set(key, value):
    with open(_cache_key(key), "w") as cache_file:
        cache_file.write(value)

    return True

def cache_get(key):
    with open(_cache_key(key)) as cache_file:
        return cache_file.read()

def cache_exists(key):
    return os.path.isfile(_cache_key(key))
