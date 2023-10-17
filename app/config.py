import logging
import secret



# DEBUG can only be set to True in a development environment for security reasons
DEBUG = True



# Database choice
MONGO_DATABASE_URI = f"mongodb+srv://{secret.userdb}:{secret.passworddb}@cluster0.9dnqbir.mongodb.net/?retryWrites=true&w=majority"
MONGO_DATABASE = 'test'
MONGO_DATABASE_ALIAS = 'core'

# Configuration of a Gmail account for sending mails
MAIL_SERVER = 'smtp.googlemail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'flask.boilerplate'
MAIL_PASSWORD = 'flaskboilerplate123'
ADMINS = ['flask.boilerplate@gmail.com']

DOMAIN_WHITELIST = ["mail.utoronto.ca"]

# Number of times a password is hashed
BCRYPT_LOG_ROUNDS = 12

LOG_LEVEL = logging.DEBUG
LOG_FILENAME = 'activity.log'
LOG_MAXBYTES = 1024
LOG_BACKUPS = 2
