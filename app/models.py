from datetime import datetime
import re

from mongoengine import Document, DynamicDocument, StringField, \
EmailField, DateTimeField, ListField, IntField, EmbeddedDocument, \
ObjectIdField, EmbeddedDocumentListField, EmbeddedDocumentField, \
ImageField, FileField
# from flask_bcrypt import generate_password_hash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from config import Config

from PIL import Image

Image.ANTIALIAS = Image.LANCZOS

from . import login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.objects(id=user_id).get()

""" Prefence object """
class Preference(Document):
    preference = StringField(required=True)
    events_with_preference = IntField(required=True, default=0)

    @staticmethod
    def get_preferences():
        return Preference.objects()
    

    # return list of (id, preference)
    @staticmethod
    def get_preferences_as_tuple():
        preferences = Preference.objects()
        tuple_preferences = []
        for preference in preferences:
            tup = (str(preference.id), preference.preference)
            tuple_preferences.append(tup)
        return tuple_preferences
    

    @staticmethod
    def get_preference_by_id(id):
        try:
            preference = Preference.objects(id=id).get()
            return preference
        except:
            return None

""" Generic User object (abstract) """
class User(UserMixin, DynamicDocument):
    creation_date = DateTimeField(default=datetime.now)

    email = EmailField(unique=True, required=True, max_length=50)
    
    # length: 8-25 characters
    # At least 1 uppercase letter
    # At least 1 lowercase letter
    # At least 1 number
    # At least 1 special character
    password_hash = StringField(required=True)

    profile_image = ImageField(size=(400,400, False), thumbnail_size=(150,150,False))


    meta = {
        'db_alias': Config.MONGODB_SETTINGS['alias'],
        'collection': 'users',
        'allow_inheritance': True
    }

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        if password == None:
            return
        regex_str="^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"
        regex = re.compile(regex_str)
        match = regex.search(password)
        if match == None:
            raise ValueError('password requirements not met')
        self.password_hash = generate_password_hash(password)


    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_mongo(self, *args, **kwargs):
        # remove the age field from the dictionary before saving it to the database
        mongo_dict = super().to_mongo(*args, **kwargs)
        mongo_dict.pop("password", None)
        return mongo_dict

    def save(self, *args, **kwargs):
        self.validate_email()
        return super().save(args, kwargs)

    def validate(self, *args, **kwargs):
        self.validate_email()
        return super().validate()

    def validate_email(self):
         # validate email properly
        email_valid = False
        email_domain = self.email.rsplit("@", 1)
        if len(email_domain) != 2:
            raise  Exception(f"'{self.email}' not a valid email (email validation failed)")
        email_domain_part = email_domain[-1].lower()
        for domain in Config.DOMAIN_WHITELIST:  
            if domain == email_domain_part:
                email_valid = True
                break
        if email_valid == False:
            raise Exception(f"'{email_domain_part}' not a valid domain (email validation failed)")
        return email_valid
    

""" Regular User """
class RegularUser(User):
    first_name = StringField(required=True, regex="^[a-zA-Z \-]+$", max_length=20)
    last_name = StringField(required=True, regex="^[a-zA-Z \-]+$", max_length=20)
    preferences = ListField(field=ObjectIdField(),required=True, default=[])

    """ List of events that the user has registered.
     Includes past and future events """
    registered_events = ListField(ObjectIdField(), default=[])

    # USER ROLES:
    #   regular - no event creation allowed
    #   organization - event creation allowed
    role = StringField(required=True, default="regular")


""" OrganizationUser """
class OrganizationUser(User):
    name = StringField(unique=True, required=True)

    # USER ROLES:
    #   regular - no event creation allowed
    #   organization - event creation allowed
    role = StringField(required=True, default="organization")

    
""" Location """
class Location(EmbeddedDocument):
    place = StringField()
    address = StringField()
    room = StringField()


""" CommentAuthor """
class UserInfo(EmbeddedDocument):
    author_id = ObjectIdField(required=True)
    name = StringField()


""" Replies to the events, 
    don't have a rating """
class Reply(EmbeddedDocument):
    # reply to either an EventComment or another reply
    content = StringField(required=True, max_length=1000)
    author = EmbeddedDocumentField(UserInfo)


""" Comments """
class Comment(Document):
    creation_date = DateTimeField(required=True, default=datetime.now())

    update_date = DateTimeField()
    event_id = ObjectIdField(required=True)
    author = EmbeddedDocumentField(UserInfo)
    content = StringField(required=True, max_length=1000)
   
    likes = IntField(min_value=0, default=0)

    rating = IntField(min_value=1, max_value=5)

    replies = EmbeddedDocumentListField(Reply)

    meta = {
        'db_alias': Config.MONGODB_SETTINGS['alias'],
        'collection': 'comments',
    }

    @staticmethod
    def get_comments_by_event_id(event_id):
        return Comment.objects(event_id=event_id)
    



class EventDate(EmbeddedDocument):
    from_date = DateTimeField(required=True)
    to_date = DateTimeField()


""" Events """
class Event(Document):
    creation_date = DateTimeField(default=datetime.now())

    update_date = DateTimeField()
    event_date = EmbeddedDocumentField(EventDate)
    location = EmbeddedDocumentField(Location)
    title = StringField(required=True)
    targeted_preferences = ListField(ObjectIdField(), required=True, default=[])
    organizer = EmbeddedDocumentField(UserInfo)
    description = StringField(required=True, max_length=1000)

    """ List of attendees, should be RegularUser objects """
    attendees = EmbeddedDocumentListField(UserInfo, default=[])

    poster = FileField()

    meta = {
        'db_alias': Config.MONGODB_SETTINGS['alias'],
        'collection': 'events'
    }

    def delete(self):
        # delete all comments
        comments = Comment.objects(event_id=self.id)
        for comment in comments:
            comment.delete()
        return super().delete()

    def validate_date(self):
        # check to make sure date from is before date to
        if self.event_date.to_date:
            if self.event_date.from_date > self.event_date.to_date:
                raise Exception(f"To date: '{self.event_date.to_date}' is earlier than From Date: '{self.event_date.from_date}'")

    def validate(self, *args, **kwargs):
        self.validate_date()
        return super().validate()
    
    def save(self, *args, **kwargs):
        self.validate_date()
        return super().save()
    
    # get recommended events based on preferences
    @staticmethod
    def get_recommended(preferences, select=4):
        # make sure events are only within the next week
        today = datetime.now()
        
        # get 4 events closest to today
        recommended_events = Event.objects(targeted_preferences__in=preferences, event_date__from_date__gte=today).order_by("+event_date__from_date")[:select]
        return recommended_events
    
    # get upcoming events
    @staticmethod
    def get_upcoming(user_id, select=4):
        today = datetime.now()

        upcoming_events = Event.objects(attendees__author_id=user_id, event_date__from_date__gte=today).order_by("+event_date__from_date")[:select]
        return upcoming_events
    
    @staticmethod
    def get_by_id(id):
        try:
            event = Event.objects(id=id).get()
            return event
        except:
            return None

    @staticmethod  
    def add_attendee(event_id, user_id, user_name):
        return Event.objects(id=event_id).update_one(push__attendees={"author_id": user_id, "name": user_name})

    @staticmethod
    def remove_attendee(event_id, user_id):
        return Event.objects(id=event_id).update_one(pull__attendees__author_id=user_id)

    @staticmethod
    def search(search=None, from_date=None, to_date=None, preferences=None, sort_by="event_date.from_date", sort_order=1, page=0, items_per_page=10):
        pipeline = []
        # append from_date if possible
        if from_date:
            pipeline.append({
                "event_date.from_date": {
                    "$lte": from_date
                }
            })

        # append to_date if possible
        if to_date:
            pipeline.append({
                "event_date.to_date": {
                    "$gte": to_date
                }
            })

        # append text search if possible
        if search:
            pipeline.append( {
                "$search": {
                    "index": "event_search",
                    "text": {
                        "query": search,
                        "path": {
                            "wildcard": "*"
                        }
                    }
                }
            })

        # append preferences if possible
        if preferences:
            pipeline.append({
                "preferences": {
                    "$all": preferences
                }
            })
        if sort_by:
            pipeline.append({
                "$sort": {
                    sort_by: sort_order
                }
            })

        # allow for paging
        start_idx = page * items_per_page
        paginated_results = [{
                "$skip": start_idx
            },
            {
                "$limit": items_per_page
            }
        ]

        pipeline.append({
            "$facet": {
                "paginated_results": paginated_results,
                "total_count": [
                    {
                        "$count": 'count'
                    }
                ]
            }
        }) 
        res = list(Event.objects().aggregate(pipeline))
        result_list = res[0]["paginated_results"]
        count = res[0]["total_count"][0]["count"]
        return result_list, count



    




