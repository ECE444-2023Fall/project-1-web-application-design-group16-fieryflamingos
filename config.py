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

    # Configuration of a Gmail account for sending mails
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = True
    MAIL_USERNAME = secret.MAIL_USERNAME
    MAIL_PASSWORD = secret.MAIL_PASSWORD
    ADMINS = ['occasional@gmail.com']
    DOMAIN_WHITELIST = ["mail.utoronto.ca"]

    FLASKY_MAIL_SUBJECT_PREFIX = '[Occasional]'
    FLASKY_MAIL_SENDER = 'Occasional <occasional@no-reply.com>'


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