import unittest
from flask import current_app
from app import create_app, db
from app.models import User

class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_user(self):
        user = User()
        user.email = "test1@mail.utoronto.ca"
        user.first_name = "Test"
        user.last_name = "Last"
        user.password = "P@assword123!"

        user = user.save()
        self.assertTrue(user == None)
