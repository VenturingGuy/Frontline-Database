import unittest
from app import app, db, bcrypt
from app.models import Mech, MechAttack, User, MechCategory

"""
Run these tests with the command:
python -m unittest app.main.tests
"""

#################################################
# Setup
#################################################

def login(client, username, password):
    return client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)

def logout(client):
    return client.get('/logout', follow_redirects=True)

def create_attacks():
    mech = Mech(name='Grendizer',
        series="UFO Robot Grendizer",
        category=MechCategory.SUPER)
    attack = MechAttack(
        name='Space Thunder',
        attack_potency=1700,
        mech=mech
    )
    db.session.add(attack)
    db.session.commit()

def create_user():
    # Creates a user with username 'VagrantGuy' and password of 'password'
    password_hash = bcrypt.generate_password_hash('password').decode('utf-8')
    user = User(username='VagrantGuy', password=password_hash)
    db.session.add(user)
    db.session.commit()

#################################################
# Tests
#################################################

class MainTests(unittest.TestCase):
 
    def setUp(self):
        """Executed prior to each test."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        db.drop_all()
        db.create_all()
 
    def test_homepage_logged_out(self):
        """Test that the relevant data shows up on the homepage."""
        # Set up
        create_user()

        # Make a GET request
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Check that page contains all of the things we expect
        response_text = response.get_data(as_text=True)
        self.assertIn('Log In', response_text)
        self.assertIn('Sign Up', response_text)

        # Check that the page doesn't contain things we don't expect
        # (these should be shown only to logged in users)
        self.assertNotIn('New Mech', response_text)
 
    def test_homepage_logged_in(self):
        """Test that the example mech shows up on the homepage."""
        # Set up
        
        create_user()
        login(self.app, 'VagrantGuy', 'password')
        create_attacks()

        # Make a GET request
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Check that page contains all of the things we expect
        response_text = response.get_data(as_text=True)
        self.assertIn('Grendizer', response_text)
        self.assertIn('VagrantGuy', response_text)
        self.assertIn('New Mech', response_text)

        # Check that the page doesn't contain things we don't expect
        # (these should be shown only to logged out users)
        self.assertNotIn('Log In', response_text)
        self.assertNotIn('Sign Up', response_text)

    def test_attack_detail_logged_out(self):
        """Test should not show details, need to be logged in to access."""
        create_user()
        response = self.app.get('/attack/1/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response_text = response.get_data(as_text=True)
        self.assertNotIn('Space Thunder', response_text)
        self.assertNotIn('1700', response_text)
        self.assertNotIn('Grendizer', response_text)

    def test_attack_detail_logged_in(self):
        """Test should show attack details as user is logged in."""
        create_user()
        login(self.app, 'VagrantGuy', 'password')
        create_attacks()
        response = self.app.get('/attack/1/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response_text = response.get_data(as_text=True)
        self.assertIn('Space Thunder', response_text)
        self.assertIn('1700', response_text)
        self.assertIn('Grendizer', response_text)

    def test_update_attack(self):
        """Test updating an attack's info."""
        # Set up
        create_attacks()
        create_user()
        login(self.app, 'VagrantGuy', 'password')

        # Make POST request with data
        post_data = {
            'name': 'Double Haken',
            'attack_potency': 1400,
        }
        self.app.post('/attack/1/1', data=post_data)
        
        # Verifies if attack has been updated.
        attacks = MechAttack.query.get(1)
        self.assertEqual(attacks.name, 'Double Haken')
        self.assertEqual(attacks.attack_potency, 1400)

    def test_new_attack(self):
        """Tests to check if a new attack is successfully created."""
        # Set up
        create_user()
        login(self.app, 'VagrantGuy', 'password')
        create_attacks()

        # Make POST request with data
        post_data = {
            'name': 'Final Dynamic Special',
            'attack_potency': 4500,
            'mech': 1
        }
        self.app.post('/new_attack', data=post_data)

        # Checks if attack was added to the corresponding mech
        created_attack = MechAttack.query.filter_by(name='Final Dynamic Special').one()
        self.assertIsNotNone(created_attack)
        self.assertEqual(created_attack.mech.name, 'Grendizer')

    def test_new_attack_logged_out(self):
        """
        Verifies is the user is redirected to the login page if trying to access the new_attack route
        while not logged in.
        """
        # Set up
        create_attacks()
        create_user()

        # Make GET request
        response = self.app.get('/new_attack')

        # Makes sure that the user was redirecte to the login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login?next=%2Fnew_attack', response.location)


