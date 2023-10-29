import unittest
from app import create_app
from app.models import User, RegularUser, OrganizationUser, Location, UserInfo, Event, Comment, EventComment, Reply

from datetime import datetime

class TestUser(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.password = 'Password@123'
        try:
            self.regular_user = RegularUser.objects(email='maryjane1@mail.utoronto.ca').get()
        except:
            self.regular_user = RegularUser(
                first_name='Mary',
                last_name='Jane',
                email='maryjane1@mail.utoronto.ca',
                password=self.password,
                preferences=['preference1', 'preference2'],
            )
            self.regular_user = self.regular_user.save()

        try:
            self.org_user = OrganizationUser.objects(email='johndoe3@mail.utoronto.ca').get()
        except:
            self.org_user = OrganizationUser(
                email='johndoe3@mail.utoronto.ca',
                password=self.password,
                name="John Doe Organization"
            )
            self.org_user = self.org_user.save() 
        
    
    def tearDown(self):
        self.regular_user.delete()
        self.org_user.delete()
        self.app_context.pop()

    def test_get(self):
        users = User.objects()
        self.assertGreaterEqual(len(users), 2)


""" for lab 5, written by Sebastian Czyrny """
class TestRegularUser(unittest.TestCase):
   
    # setup app context, create user object
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.password = 'Password@123'
        try:
            self.regular_user = RegularUser.objects(email='maryjane@mail.utoronto.ca').get()
        except:
            self.regular_user = RegularUser(
                first_name='Mary',
                last_name='Jane',
                email='maryjane@mail.utoronto.ca',
                password=self.password,
                preferences=['preference1', 'preference2'],
            )
            self.regular_user = self.regular_user.save()
       
    # delete user from database
    def tearDown(self):
        self.regular_user.delete()
        self.app_context.pop()

    def test_save_picture(self):
        with open("./tests/pic.PNG", 'rb') as picture:
            self.regular_user.profile_image.replace(picture, filename="pic.PNG") 
            self.regular_user = self.regular_user.save()
        self.assertIsNotNone(self.regular_user.profile_image)


    # fetch user, make sure it is in database, make sure it is unique
    def test_get_user(self):
        # Get user from database
        regular_user_q = RegularUser.objects(email=self.regular_user.email)
        self.assertEqual(len(regular_user_q), 1)


    # test user password
    def test_get_user_password(self):
        # Get user from database
        regular_user_q = RegularUser.objects(email=self.regular_user.email).get()
        # verify password
        verified = regular_user_q.verify_password(self.password)
        self.assertTrue(verified)

    # test user password
    def test_get_user_password_unique(self):
        # Get user from database
        regular_user1 = RegularUser(
            first_name='John',
            last_name='Doe',
            email='johndoe1@gmail.utoronto.ca',
            password='Password@123',
            preferences=['preference1', 'preference2'],
        )
        regular_user2 = RegularUser(
            first_name='John',
            last_name='Doe',
            email='johndoe@mail.utoronto.ca',
            password='Password@123',
            preferences=['preference1', 'preference2'],
        )

        self.assertNotEqual(regular_user1.password_hash, regular_user2.password_hash)

    # test invalid emails, make sure they can't validate
    def test_verify_email(self):
        regular_user1 = RegularUser(
            first_name='John',
            last_name='Doe',
            email='johndoe@gmail.com',
            password='Password@123',
            preferences=['preference1', 'preference2'],
        )

        regular_user2 = RegularUser(
            first_name='John',
            last_name='Doe',
            email='johndoe@hotmail.com',
            password='Password@123',
            preferences=['preference1', 'preference2'],
        )

        invalid = True
        try:
            regular_user1.validate()
            regular_user2.validate()
            invalid = False
        except Exception as e:
            invalid = True
        
        self.assertTrue(invalid)
    
    # test user preference query
    def test_user_preference(self):

        regular_user_q = RegularUser.objects(preferences=self.regular_user.preferences[0])
        self.assertGreaterEqual(len(regular_user_q), 1)
    

class TestOrganizationUser(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.password = 'Password123@'
        try:
            self.org_user = OrganizationUser.objects(email='johndoe2@mail.utoronto.ca').get()
        except:
            self.org_user = OrganizationUser(
                email='johndoe2@mail.utoronto.ca',
                password=self.password,
                name="John Doe Organization"
            )
            self.org_user = self.org_user.save() 

    def tearDown(self):
        self.org_user.delete()
        self.app_context.pop()


""" for Lab 5 - written by Mohammed Amir """
class TestRSVP(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.password = 'Password@123'
        try:
            self.regular_user = RegularUser.objects(email='maryjane1@mail.utoronto.ca').get()
        except:
            self.regular_user = RegularUser(
                first_name='Mary',
                last_name='Jane',
                email='maryjane1@mail.utoronto.ca',
                password=self.password,
                preferences=['preference1', 'preference2'],
            )
            self.regular_user = self.regular_user.save()

        self.event = Event(
            event_date=fixed_time,
            title='title',
            location={"place":'Place', "address":'Address', "room":'Room'},
            targeted_preferences=['preference1', 'preference2'],
            organizer={"author_id": self.org_user.id, "name": self.org_user.name},
            description='Event description',
            attendees=[{"author_id": self.org_user.id, "name": self.org_user.name}, 
                       {"author_id": self.regular_user.id, "name": self.regular_user.first_name + " " + self.regular_user.last_name}]
        )

     # delete user and event from database
        def tearDown(self):
            self.regular_user.delete()
            self.event.delete()
            self.app_context.pop()

    def testRSVP(self):
        attendee = {"author_id": self.regular_user.id, "name": self.regular_user.first_name + " " + self.regular_user.last_name}
        self.assertTrue(attendee is in self.events.attendees)
            

### for lab 5 - written by Dylan Sun 
class TestEvents(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Create a fixed datetime for testing
        fixed_time = datetime(2023, 10, 23, 12, 0)
        self.password = 'Password123@'
        try:
            self.org_user = OrganizationUser.objects(email='johndoe5@mail.utoronto.ca').get()
        except:
            self.org_user = OrganizationUser(
                email='johndoe5@mail.utoronto.ca',
                password=self.password,
                name="John Doe Organization"
            )
            self.org_user = self.org_user.save() 
        self.events = Event(
            event_date=fixed_time,
            title='title',
            location={"place":'Place', "address":'Address', "room":'Room'},
            targeted_preferences=['preference1', 'preference2'],
            organizer={"author_id": self.org_user.id, "name": self.org_user.name},
            description='Event description',
            attendees=[{"author_id": self.org_user.id, "name": self.org_user.name}]
        )

    def tearDown(self):
        self.app_context.pop()

    def test_event_date(self):
        # Test that the event_date is set to the fixed datetime
        fixed_time = datetime(2023, 10, 23, 12, 0)
        self.assertEqual(self.events.event_date, fixed_time)

    def test_location(self):
        # Test that the location attribute is set correctly
        self.assertIsInstance(self.events.location, Location)

    def test_title(self):
        # Test that the title attribute is an instance of Location
        self.assertEqual(self.events.title, 'title')
        
    def test_targeted_preferences(self):
        # Test that the targeted_preferences attribute is a list
        self.assertIsInstance(self.events.targeted_preferences, list)
        
    def test_organizer(self):
        # Test that the organizer attribute is an instance of UserInfo
        self.assertIsInstance(self.events.organizer, UserInfo)

    def test_description(self):
        # Test that the description attribute is set correctly
        self.assertEqual(self.events.description, 'Event description')

    def test_attendees(self):
        # Test that the attendees attribute is a list
        self.assertIsInstance(self.events.attendees, list)
    
    def test_file_upload(self):
        with open("./tests/pic.PNG", 'rb') as picture:
            self.events.poster.replace(picture, filename="pic.PNG") 
            self.events = self.events.save()
        self.assertIsNotNone(self.events.poster)

class TestComments(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.fixed_date = datetime(2023,10,1,0,0,0)
        self.password = 'Password123@'
        try:
            self.org_user = OrganizationUser.objects(email='johndoe1@mail.utoronto.ca').get()
        except:
            self.org_user = OrganizationUser(
                email='johndoe1@mail.utoronto.ca',
                password=self.password,
                name="John Doe Organization"
            )
            self.org_user = self.org_user.save() 
        self.event = Event(title='title',
            location={"place":'Place', "address":'Address', "room":'Room'},
            targeted_preferences=['preference1', 'preference2'],
            organizer={"author_id": self.org_user.id, "name": self.org_user.name},
            description='Event description',
            attendees=[{"author_id": self.org_user.id, "name": self.org_user.name},],
            event_date=self.fixed_date
        )
        self.event = self.event.save()
    
    def tearDown(self):
        # self.org_user.delete()
        self.app_context.pop()

    def test_add_comment(self):
        comment = EventComment(event_id=self.event.id,
            author={"author_id": self.org_user.id, "name": self.org_user.name},
            content="Pretty Cool Event!!!",
            likes=0,
            rating=3
        )
        comment = comment.save()
        self.assertIsNotNone(comment)
    
    def test_add_reply(self):
        comment = EventComment(event_id=self.event.id,
            author=self.event.organizer,
            content="Pretty Cool Event!!!",
            likes=0,
            rating=3
        )
        comment = comment.save()
        reply = Reply(event_id=self.event.id,
            author=self.event.organizer,
            content="Pretty Cool Event!!!",
            likes=0,
            reply_to_id=comment.id
        )
        reply=reply.save()
        self.assertIsNotNone(reply)
