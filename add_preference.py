from mongoengine import connect
from config import config
from app.models import Preference


connect(alias=config["testing"].MONGODB_SETTINGS["alias"], db=config["testing"].MONGODB_SETTINGS["db"], host=config["testing"].MONGODB_SETTINGS["host"])

preferences = ["Academic", "Cultural", "Extra-Curricular", "Health", "Science", "Math", "Business", "Languages", "Art", "Music", "Sports"]

for preference in preferences:
    p = Preference(preference=preference)
    p.save()