import redis

class RedisMemory:
    def __init__(self, host="redis", port=6379):  # ← use service name "redis"
        self.client = redis.Redis(host=host, port=port, decode_responses=True)

    def set(self, key: str, value: str):
        self.client.set(key, value)

    def get(self, key: str):
        return self.client.get(key)
