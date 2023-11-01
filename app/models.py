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
    preferences = ListField(required=True, default=[])

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


""" Comments """
class Comment(Document):
    creation_date = DateTimeField(required=True, default=datetime.now())

    update_date = DateTimeField()
    event_id = ObjectIdField(required=True)
    author = EmbeddedDocumentField(UserInfo)
    content = StringField(required=True, max_length=1000)
   
    likes = IntField(min_value=0, default=0)

    meta = {
        'db_alias': Config.MONGODB_SETTINGS['alias'],
        'collection': 'comments',
        'allow_inheritance': True,
    }

   


""" Comment for the actual event"""
class EventComment(Comment):
    rating = IntField(min_value=1, max_value=5)
    

""" Replies to the events, 
    don't have a rating """
class Reply(Comment):
    # reply to either an EventComment or another reply
    reply_to_id = ObjectIdField(required=True)


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
    targeted_preferences = ListField(StringField(), required=True, default=[])
    organizer = EmbeddedDocumentField(UserInfo)
    description = StringField(required=True, max_length=1000)

    """ List of attendees, should be RegularUser objects """
    attendees = EmbeddedDocumentListField(UserInfo, required=True, default=[])

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
            if self.event_date.from_date < self.event_date.to_date:
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

    




