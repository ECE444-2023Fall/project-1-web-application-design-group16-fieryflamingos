from datetime import datetime
import re

from mongoengine import Document, DynamicDocument, StringField, \
EmailField, DateTimeField, ListField, IntField, EmbeddedDocument, \
ObjectIdField, EmbeddedDocumentListField, EmbeddedDocumentField, \
ImageField, FileField
# from flask_bcrypt import generate_password_hash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from bson.objectid import ObjectId
from config import Config

from .util import validate_email

from PIL import Image

Image.ANTIALIAS = Image.LANCZOS

from . import login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.get_user_by_id(user_id)

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
            tup = (preference.preference, str(preference.id), preference.events_with_preference)
            tuple_preferences.append(tup)
        return tuple_preferences
    

    @staticmethod
    def get_preference_by_id(id):
        try:
            preference = Preference.objects(id=id).get()
            return preference
        except:
            return None
        
    @staticmethod
    def inc_event_count(preference_id, inc=1):
        try:
            Preference.objects(id=preference_id).update_one(inc__events_with_preference=inc)
        except Exception as e:
            print(e)
            pass
    @staticmethod
    def inc_events_count(preference_ids, inc=1):
        try:
            Preference.objects(id__in=preference_ids).update(inc__events_with_preference=inc)
        except Exception as e:
            print(e)
            pass
    

""" Generic User object (abstract) """
class User(UserMixin, DynamicDocument):
    creation_date = DateTimeField(default=datetime.now)

    email = EmailField(required=True, max_length=50)
    
    # length: 8-25 characters
    # At least 1 uppercase letter
    # At least 1 lowercase letter
    # At least 1 number
    # At least 1 special character
    password_hash = StringField(required=True)

    profile_image = ImageField(size=(400,400, False), thumbnail_size=(150,150,False))

    username = StringField(unique=True, required=True)

    meta = {
        'db_alias': Config.MONGODB_SETTINGS['alias'],
        'collection': 'users',
        'allow_inheritance': True,
        "auto_create_index": False
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
        
        return validate_email(self.email)
    
    @staticmethod
    def get_user_by_username(username):
        try:
            user = User.objects(username=username).get()
            return user
        except:
            return None
    
    @staticmethod 
    def get_user_by_id(user_id):
        try:
            user = User.objects(id=user_id).exclude("password_hash").get()
            return user
        except:
            return None

    

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

    @staticmethod
    def add_event(user_id, event_id):
        RegularUser.objects(id=user_id).update_one(add_to_set__registered_events=event_id)

    @staticmethod
    def remove_event(user_id, event_id):
        RegularUser.objects(id=user_id).update_one(pull__registered_events=event_id)


""" OrganizationUser """
class OrganizationUser(User):
    name = StringField(unique=True, required=True)

    # USER ROLES:
    #   regular - no event creation allowed
    #   organization - event creation allowed
    role = StringField(required=True, default="organization")


    @staticmethod
    def get_by_id(id):
        try:
            user = OrganizationUser.objects(id=id).exclude("password_hash").get()
            return user
        except:
            return None

    
""" Location """
class Location(EmbeddedDocument):
    place = StringField()
    address = StringField()
    room = StringField()


""" CommentAuthor """
class UserInfo(EmbeddedDocument):
    author_id = ObjectIdField(required=True)
    email = StringField()
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
    content = StringField(required=True, max_length=10000)
   
    likes = IntField(min_value=0, default=0)

    rating = IntField(min_value=1, max_value=5)

    replies = EmbeddedDocumentListField(Reply)

    meta = {
        'db_alias': Config.MONGODB_SETTINGS['alias'],
        'collection': 'comments',
    }

    @staticmethod
    def get_comments_by_event_id(event_id):
        return Comment.objects(event_id=event_id).order_by("+creation_date")

    @staticmethod 
    def get_comment_by_id(id):
        try:
            comment = Comment.objects(id=id).get()
            return comment
        except:
            return None
    
    @staticmethod
    def add_reply(event_id, reply):
        Comment.objects(id=event_id).update_one(push__replies=reply)
    



class EventDate(EmbeddedDocument):
    from_date = DateTimeField(required=True)
    to_date = DateTimeField()


""" Events """
class Event(Document):
    creation_date = DateTimeField(default=datetime.now())

    update_date = DateTimeField()
    registration_open_until = DateTimeField()
    event_date = EmbeddedDocumentField(EventDate)
    location = EmbeddedDocumentField(Location)
    title = StringField(required=True)
    targeted_preferences = ListField(ObjectIdField(), required=True, default=[])
    organizer = EmbeddedDocumentField(UserInfo)
    description = StringField(required=True, max_length=10000)

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
        recommended_events = Event.objects(targeted_preferences__in=preferences, event_date__from_date__gte=today) \
            .exclude("attendees", "description") \
            .order_by("+event_date__from_date")[:select]
        return recommended_events
    
    # get upcoming events
    @staticmethod
    def get_upcoming(user_id, select=4):
        today = datetime.now()

        upcoming_events = Event.objects(attendees__author_id=user_id, event_date__from_date__gte=today) \
            .exclude("attendees", "description") \
            .order_by("+event_date__from_date")[:select]
        return upcoming_events
    
    @staticmethod
    def get_by_id(id):
        try:
            event = Event.objects(id=id).get()
            return event
        except:
            return None

    @staticmethod  
    def add_attendee(event_id, user_id, email, user_name):
        attendee = UserInfo(author_id=user_id, email=email, name=user_name)
        return Event.objects(id=event_id).update_one(push__attendees=attendee)

    @staticmethod
    def remove_attendee(event_id, user_id):
        return Event.objects(id=event_id).update_one(pull__attendees__author_id=user_id)

    @staticmethod
    def search(search=None, start_date=None, end_date=None, preferences=None, sort_by="event_date.from_date", sort_order=1, page=0, items_per_page=10):
        pipeline = []

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

        # append from_date if possible
        if start_date:
            pipeline.append({ "$match": {
                    'event_date.from_date': {
                        '$gte': datetime.strptime(start_date, "%Y-%m-%d"),
                    }
                }
            })
        if end_date:
            pipeline.append({ "$match": {
                    'event_date.from_date': {
                        '$lte': datetime.strptime(end_date, "%Y-%m-%d"),
                    }
                }
            })

        # append preferences if possible
        if preferences:
            
            pipeline.append({
                "$match": {
                    "targeted_preferences": {
                        "$all": [ObjectId(preference) for preference in preferences]
                    }
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
            "$unset": [ 'attendees', 'description', 'targeted_preferences']
        })

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
        for result in result_list:
            if (str(result["_id"])):
                result["link"] = '/event/' + str(result["_id"])
        count = res[0]["total_count"]
        if count:
            count = count[0]["count"]
        else:
            count = 0
        return result_list, count


    @staticmethod
    def get_summary_from_list_future(id_list):
        today = datetime.now()
        return Event.objects(id__in=id_list, event_date__from_date__gte=today).exclude("attendees", "description",  "targeted_preferences")
    
    @staticmethod
    def get_summary_from_list_past(id_list):
        today = datetime.now()
        return Event.objects(id__in=id_list, event_date__from_date__lt=today).exclude("attendees", "description",  "targeted_preferences")
    
    @staticmethod
    def get_organization_events_future(org_id):
        today = datetime.now()
        return Event.objects(organizer__author_id=org_id, event_date__from_date__gte=today).order_by("+event_date.from_date").exclude("attendees", "description",  "targeted_preferences")
    
    @staticmethod
    def get_organization_events_past(org_id):
        today = datetime.now()
        return Event.objects(organizer__author_id=org_id, event_date__from_date__lt=today).order_by("+event_date.from_date").exclude("attendees", "description", "targeted_preferences")
    




