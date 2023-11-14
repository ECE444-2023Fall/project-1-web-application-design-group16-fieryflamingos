import unittest
from app import create_app
from app.models import User, RegularUser, OrganizationUser, Event, EventComment, Reply
from datetime import datetime

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_user_and_event_interaction(self):
        # Create a regular user
        regular_user = RegularUser(
            first_name='Mary',
            last_name='Jane',
            email='maryjane1@mail.utoronto.ca',
            password='Password@123',
            preferences=['preference1', 'preference2'],
        )
        regular_user.save()

        # Create an event organized by the regular user
        fixed_time = datetime(2023, 10, 23, 12, 0)
        event = Event(
            event_date={"from_date": fixed_time, "to_date": fixed_time},
            title='Integration Test Event',
            location={"place": 'Place', "address": 'Address', "room": 'Room'},
            targeted_preferences=['preference1', 'preference2'],
            organizer={"author_id": regular_user.id, "name": regular_user.get_full_name()},
            description='Event description',
            attendees=[{"author_id": regular_user.id, "name": regular_user.get_full_name()}]
        )
        event.save()

        # Fetch the user and check if the event is associated with the user
        fetched_user = User.objects(email=regular_user.email).get()
        self.assertIn(event.id, fetched_user.attending_events)

    def test_event_and_comment_interaction(self):
        # Create an event
        fixed_time = datetime(2023, 10, 23, 12, 0)
        event = Event(
            event_date={"from_date": fixed_time, "to_date": fixed_time},
            title='Integration Test Event',
            location={"place": 'Place', "address": 'Address', "room": 'Room'},
            targeted_preferences=['preference1', 'preference2'],
            organizer={"author_id": 1, "name": "Test Organizer"},
            description='Event description',
            attendees=[]
        )
        event.save()

        # Add a comment to the event
        comment = EventComment(
            event_id=event.id,
            author={"author_id": 1, "name": "Test User"},
            content="Integration Test Comment",
            likes=0,
            rating=5
        )
        comment.save()

        # Fetch the event and check if the comment is associated with the event
        fetched_event = Event.objects(title='Integration Test Event').get()
        self.assertIn(comment.id, fetched_event.comments)

    def test_organization_user_and_event_interaction(self):
        # Create an organization user
        org_user = OrganizationUser(
            email='johndoe_org@mail.utoronto.ca',
            password='Password@123',
            name='Test Organization'
        )
        org_user.save()

        # Create an event organized by the organization user
        fixed_time = datetime(2023, 10, 23, 12, 0)
        event = Event(
            event_date={"from_date": fixed_time, "to_date": fixed_time},
            title='Integration Test Event',
            location={"place": 'Place', "address": 'Address', "room": 'Room'},
            targeted_preferences=['preference1', 'preference2'],
            organizer={"author_id": org_user.id, "name": org_user.name},
            description='Event description',
            attendees=[]
        )
        event.save()

        # Fetch the user and check if the event is associated with the organization user
        fetched_org_user = OrganizationUser.objects(email=org_user.email).get()
        self.assertIn(event.id, fetched_org_user.organized_events)
    
    def test_event_and_reply_interaction(self):
        # Create an event
        fixed_time = datetime(2023, 10, 23, 12, 0)
        event = Event(
            event_date={"from_date": fixed_time, "to_date": fixed_time},
            title='Integration Test Event',
            location={"place": 'Place', "address": 'Address', "room": 'Room'},
            targeted_preferences=['preference1', 'preference2'],
            organizer={"author_id": 1, "name": "Test Organizer"},
            description='Event description',
            attendees=[]
        )
        event.save()

        # Add a comment to the event
        comment = EventComment(
            event_id=event.id,
            author={"author_id": 1, "name": "Test User"},
            content="Integration Test Comment",
            likes=0,
            rating=5
        )
        comment.save()

        # Add a reply to the comment
        reply = Reply(
            event_id=event.id,
            author={"author_id": 1, "name": "Test User"},
            content="Integration Test Reply",
            likes=0,
            reply_to_id=comment.id
        )
        reply.save()

        # Fetch the event and check if the reply is associated with the comment
        fetched_event = Event.objects(title='Integration Test Event').get()
        fetched_comment = EventComment.objects(content='Integration Test Comment').get()
        self.assertIn(reply.id, fetched_comment.replies)

if __name__ == '__main__':
    unittest.main()
