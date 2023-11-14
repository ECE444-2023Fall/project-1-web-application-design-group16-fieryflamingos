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

    

if __name__ == '__main__':
    unittest.main()
