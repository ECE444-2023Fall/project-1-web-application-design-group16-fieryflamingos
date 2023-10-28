import unittest
from app import create_app
from app.models import User, RegularUser, OrganizationUser, Location, UserInfo, Events

from datetime import datetime


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
        picture = open("./tests/pic.PNG", 'rb')
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
        self.organization_user = OrganizationUser(
            name='Organization',
            email='org@example.com',
            password='Password@123',
            events=[]
        )

    def tearDown(self):
        self.app_context.pop()

    def test_events_defaultValue(self):
        self.assertEqual(self.organization_user.events, [])


### for lab 5 - written by Dylan Sun 
class TestEvents(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Create a fixed datetime for testing
        fixed_time = datetime(2023, 10, 23, 12, 0)

        self.events = Events(
            event_date=fixed_time,
            location='Location',
            title=Location(place='Place', address='Address', room='Room'),
            targeted_preferences=['preference1', 'preference2'],
            organizer=UserInfo(author_id='123', name='John Doe'),
            description='Event description',
            attendees=[UserInfo(author_id='456', name='Jane Smith')]
        )

    def tearDown(self):
        self.app_context.pop()

    def test_event_date(self):
        # Test that the event_date is set to the fixed datetime
        fixed_time = datetime(2023, 10, 23, 12, 0)
        self.assertEqual(self.events.event_date, fixed_time)

    def test_location(self):
        # Test that the location attribute is set correctly
        self.assertEqual(self.events.location, 'Location')

    def test_title(self):
        # Test that the title attribute is an instance of Location
        self.assertIsInstance(self.events.title, Location)
        
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


