import json

import redis

redis_client = redis.Redis(
    host="167.71.142.207", port=6379, db=0
)

print("redis client connected successful.. ", redis_client)

def get(key):
    value = redis_client.get(key)
    if value:
        return json.loads(value)
    else:
        return None

def set_user_cache(key, value):
    value = json.dumps(value)
    redis_client.set(key, value)


def delete(key):
    redis_client.delete(key)
