import unittest
from flask import current_app
from app import create_app, db
from app.models import User, RegularUser, OrganizationUser, Location, UserInfo, Reply, Comment, Events

from datetime import datetime
from mongoengine import connect

class TestUser(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.user = RegularUser(
            first_name='John',
            last_name='Doe',
            email='johndoe@example.com',
            password='Password@123',
            preferences=['preference1', 'preference2'],
            registered_events=[]
        )

    def tearDown(self):
        self.app_context.pop()

    def test_validate_email_validEmail(self):
        result = self.user.validate_email()
        self.assertTrue(result)

    def test_validate_email_invalidEmail(self):
        self.user.email = 'invalid'
        self.assertRaises(Exception, self.user.validate_email)

    def test_save_passwordHashed(self):
        self.user.save()
        self.assertNotEqual(self.user.password, 'Password@123')

    def test_validate_password_valid(self):
        self.assertTrue(self.user.validate_password('Password@123'))

    def test_validate_password_invalid(self):
        self.assertFalse(self.user.validate_password('password'))
class TestRegularUser(unittest.TestCase):
   
        
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.regular_user = RegularUser(
            first_name='John',
            last_name='Doe',
            email='johndoe@example.com',
            password='Password@123',
            preferences=['preference1', 'preference2'],
            registered_events=[]
        )

    def tearDown(self):
        self.app_context.pop()

    def test_registered_events_defaultValue(self):
        self.assertEqual(self.regular_user.registered_events, [])

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

class TestComment(unittest.TestCase):
        
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.comment = Comment(
            author=UserInfo(author_id='123', name='John Doe'),
            content='This is a comment',
            rating=4,
            replies=[]
        )

    def tearDown(self):
        self.app_context.pop()

    def test_replies_defaultValue(self):
        self.assertEqual(self.comment.replies, [])



class TestEvents(unittest.TestCase):

        
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.events = Events(
            event_date=datetime.now(),
            location='Location',
            title=Location(place='Place', address='Address', room='Room'),
            targeted_preferences=['preference1', 'preference2'],
            organizer=UserInfo(author_id='123', name='John Doe'),
            description='Event description',
            attendees=[UserInfo(author_id='456', name='Jane Smith')],
            comments=[]
        )

    def tearDown(self):
        self.app_context.pop()

    def test_comments_defaultValue(self):
        self.assertEqual(self.events.comments, [])

