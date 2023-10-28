from datetime import datetime

from mongoengine import Document, StringField, EmailField, \
    DateTimeField, ListField, IntField, EmbeddedDocument, \
    ObjectIdField, EmbeddedDocumentListField, EmbeddedDocumentField, \
    ImageField, FileField
from flask_bcrypt import generate_password_hash

from config import Config

class User(Document):
    creation_date = DateTimeField(default=datetime.now)

    email = EmailField(unique=True, required=True, max_length=50)
    
    # length: 8-25 characters
    # At least 1 uppercase letter
    # At least 1 lowercase letter
    # At least 1 number
    # At least 1 special character
    password = StringField(required=True, regex="^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[@#$%^&+=]).{8,25}$", min_length=10)

    profile_image = ImageField(size=(400,400, False), thumbnail_size=(150,150,False))


    meta = {
        'db_alias': Config.MONGODB_SETTINGS['alias'],
        'collection': 'users',
        'allow_inheritance': True,
        'abstract': True
    }

    def save(self, *args, **kwargs):
        self.password = generate_password_hash(password=self.password).decode("utf-8")
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

    """ Events the organization has organized """
    events = ListField(ObjectIdField(), default=[])

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
    name = StringField(regex="^[a-zA-Z \-]+$", max_length=50)


""" Comments """
class Comment(Document):
    creation_date = DateTimeField(required=True, default=datetime.now())

    update_date = DateTimeField()
    author = EmbeddedDocumentField(UserInfo)
    content = StringField(required=True, max_length=1000)
   
    likes = IntField(min_value=0, default=0)

    meta = {
        'db_alias': Config.MONGODB_SETTINGS['alias'],
        'collection': 'comments',
        'allow_inheritance': True,
        'abstract': True
    }


""" Comment for the actual event"""
class EventComment(Comment):
    event_id = ObjectIdField(rqeuired=True)
    rating = IntField(required=True, min_value=1, max_value=5)
    

""" Replies to the events, 
    don't have a rating """
class Reply(Comment):
    # reply to either an EventComment or another reply
    reply_to_id = ObjectIdField(required=True)


""" Events """
class Events(Document):
    creation_date = DateTimeField(default=datetime.now())

    update_date = DateTimeField()
    event_date = DateTimeField(required=True)
    location = StringField(required=True)
    title = EmbeddedDocumentField(Location)
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


