import mongoengine
import config

def db_init():
    print("setting up Database...")
    mongoengine.connect(alias=config.MONGO_DATABASE_ALIAS, db=config.MONGO_DATABASE, host=config.MONGO_DATABASE_URI)
    print("Done initializing database...")


def db_disconnect():
    print("Dropping Database connection...")
    mongoengine.disconnect(alias=config.MONGO_DATABASE_ALIAS)
    print("Successfully disconnected from database...")

