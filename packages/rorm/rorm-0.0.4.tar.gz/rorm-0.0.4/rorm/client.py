import redis
from .settings import *


class Redis:

    redis_conf = REDIS['default']
    redis_host = redis_conf['HOST']
    redis_port = redis_conf['PORT']
    redis_pool = redis.ConnectionPool(
        host=redis_host, port=redis_port, db=0)

    @classmethod
    def get_client(cls):
        return redis.Redis(connection_pool=cls.redis_pool)


class Client:
    """
    Used as interface in all other modules.
    """
    instance = Redis  # overwrite this for mocking

    @classmethod
    def get_client(cls):
        return cls.instance.get_client()
