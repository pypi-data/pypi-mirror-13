class Lock:

    def __init__(self, config, pattern):
        self.pattern = pattern
        self.config = config

    def add(self, channel, user, category, timestamp):
        '''Add a system wide lock
        This lock is applicable to everyone sharing this Redis system.
        '''
        key = self.key(channel, user, category)
        self.config.redis.lpush(key, timestamp)
        self.config.redis.ltrim(key, 0, self.config.cache_size)

    def key(self, channel, user, category):
        return self.pattern % (self.config.namespace, channel, user, category)

    def get(self, channel, user, category):
        '''Find a lock
        This gets first element from the list.
        '''
        key = self.key(channel, user, category)
        return self.config.redis.lindex(key, 0)

    def list(self):
        pattern = "%s:l:*" % self.config.namespace
        keys = self.config.redis.keys(pattern)
        return keys

    def remove(self, channel, user, category):
        rule_key = self.key_pattern % (self.key_namespace, channel, user, category)
        config.redis.delete(rule_key)
