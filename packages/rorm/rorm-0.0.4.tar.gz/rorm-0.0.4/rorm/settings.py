import redis
import os

REDIS = {
    'default': {
        'HOST': os.environ.get('DOCKER_REDIS'),
        'PORT': 6379,
        'DB': 0,
    }
}
