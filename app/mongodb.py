from mongoengine import connect

class MongoEngine():

    def init_app(self, app):
        connect(alias=app.config["MONGODB_SETTINGS"]["alias"], db=app.config["MONGODB_SETTINGS"]["db"], host=app.config["MONGODB_SETTINGS"]["host"])


