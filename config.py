import os

import logging
import secret

basedir = os.path.abspath(os.path.dirname(__file__))
class Config:
    MONGODB_SETTINGS = {
        "host": f"mongodb+srv://{secret.MONGO_USERNAME}:{secret.MONGO_PASSWORD}@cluster0.9dnqbir.mongodb.net/?retryWrites=true&w=majority",
        "alias": "default",
    }
  
    SECRET_KEY = secret.SECRET_KEY

  
    DOMAIN_WHITELIST = ["mail.utoronto.ca"]


    # Number of times a password is hashed
    BCRYPT_LOG_ROUNDS = 12

    LOG_LEVEL = logging.DEBUG
    LOG_FILENAME = 'activity.log'
    LOG_MAXBYTES = 1024
    LOG_BACKUPS = 2


    @staticmethod
    def init_app(app):
        pass
class DevelopmentConfig(Config):
    DEBUG = True
    MONGODB_SETTINGS = {
        'db': 'test',
        "host": f"mongodb+srv://{secret.MONGO_USERNAME}:{secret.MONGO_PASSWORD}@cluster0.9dnqbir.mongodb.net/?retryWrites=true&w=majority",
        "alias": "default",
    }


class TestingConfig(Config):
    TESTING = True
    MONGODB_SETTINGS = {
        'db': 'test',
        "host": f"mongodb+srv://{secret.MONGO_USERNAME}:{secret.MONGO_PASSWORD}@cluster0.9dnqbir.mongodb.net/?retryWrites=true&w=majority",
        "alias": "default",
    }

class ProductionConfig(Config):
    DEBUG = False
    MONGODB_SETTINGS = {
        'db': 'prod',
        "host": f"mongodb+srv://{secret.MONGO_USERNAME}:{secret.MONGO_PASSWORD}@cluster0.9dnqbir.mongodb.net/?retryWrites=true&w=majority",
        "alias": "default",
    }

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}