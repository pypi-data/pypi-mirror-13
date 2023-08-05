import redis

config = None

class Config:
    def __init__(self, host, port, db):
        self.redis = redis.StrictRedis(host, port, db)
        self.rule = None
        self.lock = None
        self.namespace = None
        self.cache_size = None
