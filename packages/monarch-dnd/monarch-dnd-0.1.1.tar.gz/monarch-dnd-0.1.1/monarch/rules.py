'''Rule helper class'''
class Rule:
    def __init__(self, config, pattern):
        self.pattern = pattern
        self.config = config

    def add(self, channel, category, cooldown):
        '''Add a system wide rule
        This rule is applicable to everyone sharing this Redis system.
        '''
        if channel and category and cooldown:
            key = self.pattern % (self.config.namespace, channel, category)
            return self.config.redis.set(key, cooldown)
        else:
            raise TypeError

    def key(self, channel, category):
        '''Redis Key for the rule'''
        return self.pattern % (self.config.namespace, channel, category)

    def get(self, channel, category):
        '''Cool down values for Rule.
        All values should be in minutes'''
        key = self.key(channel, category)
        return self.config.redis.get(key)

    def list(self):
        '''List of all the rules
        For unittests'''
        pattern = "%s:r:*" % self.config.namespace
        keys = self.config.redis.keys(pattern)
        return keys

    def remove(self, channel, category):
        rule_key = self.pattern % (self.config.namespace, channel, category)
        self.config.redis.delete(rule_key)
