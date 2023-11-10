from mongoengine import connect
from config import config
from app.models import Preference, OrganizationUser, User, Event, Comment, RegularUser


import random
from datetime import datetime

connect(alias=config["testing"].MONGODB_SETTINGS["alias"], db=config["testing"].MONGODB_SETTINGS["db"], host=config["testing"].MONGODB_SETTINGS["host"])

# preferences = ["Academic", "Cultural", "Extra-Curricular", "Health", "Science", "Math", "Business", "Languages", "Art", "Music", "Sports"]

# for preference in preferences:
#     p = Preference(preference=preference)
#     p.save()

# users = OrganizationUser.objects()
# regular_users = RegularUser.objects()

# users = [org_user1, org_user2, org_user3 ]



# A fixed date for demonstration purposes
# fixed_dates = [(datetime(2023, 11, 7, 5), datetime(2023, 11, 7, 6)), (datetime(2023, 12, 7, 5), datetime(2023, 12, 7, 6)), (datetime(2023, 1, 2, 12), datetime(2023, 1, 2, 13)), (datetime(2023, 12, 25, 12), datetime(2023, 12, 25, 13)), (datetime(2023, 1, 31, 22), datetime(2023, 1, 31, 23))]

# # A list of possible places, addresses and rooms
# places = ["Library", "Cafeteria", "Gym", "Auditorium", "Classroom"]
# addresses = ["123 Main Street", "456 Queen Street", "789 King Street", "1011 College Street", "1213 University Avenue"]
# rooms = ["A101", "B202", "C303", "D404", "E505"]

# # A list of possible event titles and descriptions
# titles = ["Book Club Meeting", "Lunch Special", "Basketball Game", "Musical Performance", "Coding Workshop"]
# descriptions = ["Join us for a discussion of the latest bestseller.", "Enjoy a delicious meal for only $5.", "Cheer on your favorite team in a thrilling match.", "Listen to the talented students of the music department.", "Learn the basics of Python programming in a fun and interactive way."]


# A list of possible comment contents
# contents = ["Pretty cool event!!!", "I had a great time.", "This was boring.", "The food was terrible.", "The music was amazing.", "The speaker was very knowledgeable.", "The game was exciting.", "The workshop was very helpful.", "The book was interesting.", "The event was well-organized."]

# preferences = Preference.objects()
# preferences = [preference.id for preference in preferences]

preferences = Preference.objects()
pref_ids = [preference.id for preference in preferences]

# A loop to generate 35 events
# events = Event.objects()
# for event in events:
#   num_prefs = random.randint(1,5)
#   prefs = random.sample(pref_ids, num_prefs)

#   for preference in prefs:
#     Preference.inc_event_count(preference)
  
#   Event.objects(id=event.id).update_one(targeted_preferences=prefs)

RegularUser.objects(username="s.czyrny").update_one(preferences=pref_ids)
