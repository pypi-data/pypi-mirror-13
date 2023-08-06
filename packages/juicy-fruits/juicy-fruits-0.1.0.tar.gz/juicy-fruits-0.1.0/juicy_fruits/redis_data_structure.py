
import redis_collections

class RedisDataStructure(object):

    def __init__(self, db):
        self.db = db

    def List(self, key):
        return redis_collections.List(key=key, redis=self.db)

    def Dict(self, key):
        return redis_collections.Dict(key=key, redis=self.db)

    def Set(self, key):
        return redis_collections.Set(key=key, redis=self.db)