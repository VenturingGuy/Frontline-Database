import unittest

from app import app, db, bcrypt
from app.models import User

"""
Run these tests with the command:
python -m unittest app.auth.tests
"""

#################################################
# Setup
#################################################


def create_user():
    password_hash = bcrypt.generate_password_hash("password").decode("utf-8")
    user = User(username="VagrantGuy", password=password_hash)
    db.session.add(user)
    db.session.commit()


#################################################
# Tests
#################################################


class AuthTests(unittest.TestCase):
    """Tests for authentication (login & signup)."""

    def setUp(self):
        """Executed prior to each test."""
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app = app.test_client()
        db.drop_all()
        db.create_all()

    def test_signup(self):
        """Tests new user signup."""
        post_data = {"username": "username1", "password": "newpass1"}
        self.app.post("/signup", data=post_data)
        signedup_user = User.query.filter_by(username="username1").one()
        self.assertEqual(signedup_user.username, "username1")

    def test_signup_existing_user(self):
        """Attempts to signup existing user, throws error since username is taken."""
        create_user()
        post_data = {"username": "VagrantGuy", "password": "newpass1"}
        response = self.app.post("/signup", data=post_data)
        response_text = response.get_data(as_text=True)
        self.assertIn(
            "That username is taken. Please choose a different one.", response_text
        )

    def test_login_correct_password(self):
        """Tests standard login."""
        create_user()
        post_data = {"username": "VagrantGuy", "password": "password"}
        response = self.app.post("/login", data=post_data)

        response_text = response.get_data(as_text=True)
        self.assertNotIn("Log In", response_text)
        self.assertNotIn("Sign Up", response_text)

    def test_login_nonexistent_user(self):
        """Tests login with nonexistent user, throws error because no such user exists."""
        post_data = {"username": "username1", "password": "password_hash"}
        response = self.app.post("/login", data=post_data)
        response_text = response.get_data(as_text=True)
        self.assertIn("No user with that username. Please try again.", response_text)

    def test_login_incorrect_password(self):
        """Tets user login with wrong password, throws error because password is incorrect."""
        create_user()
        post_data = {"username": "VagrantGuy", "password": "fakepass1"}
        response = self.app.post("/login", data=post_data)
        response_text = response.get_data(as_text=True)
        self.assertIn("Password does not match. Please try again.", response_text)

    def test_logout(self):
        """Tests a typical logout instance."""
        create_user()
        password_hash = bcrypt.generate_password_hash("password").decode("utf-8")
        post_data = {"username": "username1", "password": password_hash}
        self.app.post("/login", data=post_data)
        response = self.app.get("/logout", follow_redirects=True)

        response_text = response.get_data(as_text=True)
        self.assertIn("Log In", response_text)
        self.assertIn("Sign Up", response_text)