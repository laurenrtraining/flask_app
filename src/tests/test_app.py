import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Similar to what I needed to do in app.py, this line ensures the test file looks in the correct place for app

from app import app
from database.database import db, Staff, Societies, Staff_Societies,Date_Availability


# Using PyTest is very new to me, and I used the PyTest pages to help, therefore there are many comments to help me understand what is going on (Pytest, 2025).
# Unlike Jest, PyTest only works with backend code - this took me a while to understand that I didn't need to test button clicks, just the database functionality.

@pytest.fixture
# This client function simulates the database and prevents tests against real data
def client():
    app.config['TESTING'] = True # States that the app is in testing mode
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'

    with app.app_context():
        db.create_all()
        yield app.test_client()
    
# RENDER INDEX PAGE ON STARTUP
def test_render_index_when_logged_out(client):
    # GIVEN a logged-in staff user in the session
    # WHEN the index page is requested
    # THEN the response should be successful and contain the staff_username (Kennedy, 2023)
    response = client.get('/', follow_redirects=True)
    assert response.status_code == 200
    assert b'Guest' in response.data


# TESTS THAT USER CAN SIGN IN AS NON ADMIN SUCCESSFULLY AND THAT THE DB SEARCH WORKS
def test_user_sign_in_success_NON_ADMIN(client):
    # Gets to the sign in page first
    response = client.get('/sign_in.html')
    assert response.status_code == 200

    staff = Staff(staff_username='test_user', job_role='Non Admin', staff_email='test_user@staff.uk', password='testUser123')
    db.session.add(staff)
    db.session.commit()

    response = client.post('/sign_in.html', data={'staff_username':'test_user', 'password':'testUser123'}, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Account' in response.data

# TESTS THAT USER CAN SIGN IN AS ADMIN SUCCESSFULLY AND THAT THE DB SEARCH WORKS
def test_user_sign_in_success_ADMIN(client):
    # Gets to the sign in page first
    response = client.get('/sign_in.html')
    assert response.status_code == 200

    staff = Staff(staff_username='test_user2', job_role='Admin', staff_email='test_user2@staff.uk', password='testUser456')
    db.session.add(staff)
    db.session.commit()

    response = client.post('/sign_in.html', data={'staff_username':'test_user2', 'password':'testUser456'}, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Admin Account' in response.data

# TESTS THAT VALIDATION WORKS BY INPUTTING INCORRECT PASSWORD
def test_user_sign_in_fail(client):
    # Gets to the sign in page first
    response = client.get('/sign_in.html')
    assert response.status_code == 200

    staff = Staff(staff_username='test_user', job_role='test_role', staff_email='test_user@staff.uk', password='testUser123')
    db.session.add(staff)
    db.session.commit()

    response = client.post('/sign_in.html', data={'staff_username':'test_user', 'password':'wrongPassword123'}, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data


# TESTS THAT USER REGISTRATION SUCCESSFULLY HITS AND ADDS TO THE DATABASE
def test_user_registration_if_existing(client):
    # Gets to the sign in page first
    response = client.get('/sign_in.html')
    assert response.status_code == 200

    staff = Staff(staff_username='test_user', job_role='test_role', staff_email='test_user@staff.uk', password='testUser123')
    db.session.add(staff)
    db.session.commit()

    # Confirm registration option is on the page
    assert b'Register' in response.data

    # Simulates clicking registration button
    response = client.get('/register.html')
    assert response.status_code == 200
    assert b'Registration Form' in response.data

    response = client.post('/register.html', data={'staff_username':'test_user1', 'job_role':'test_role2', 'staff_email':'test_user@staff.uk', 'password':'testUser1234'}, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Email already registered. Please sign in.' in response.data



# TESTS THAT USERS CAN CREATE NEW GROUPS
def test_create_groups(client):
    # Logs in a user
    staff = Staff(staff_username='test_user', job_role='Non Admin', staff_email='test_user@staff.uk', password='testUser123')
    db.session.add(staff)
    db.session.commit()

    response = client.post('/sign_in.html', data={'staff_username':'test_user', 'password':'testUser123'}, follow_redirects=True)
    assert response.status_code == 200
    #  Log in successful

    # Simulates staff session
    staff_id = staff.staff_id

    with client.session_transaction() as session:
        session['user_id'] = staff_id
        session['staff_username'] = staff.staff_username
        session['job_role'] = staff.job_role

    # Gets to create group page
    response = client.post('/submit-group', data={'name':'test_group', 'description':'test description'}, follow_redirects=True)
    assert response.status_code == 200

    response = client.get('/')
    assert response.status_code == 200
    assert b'test_group' in response.data
    # Creates new group successfully















# # Just do a couple of tests
# # Pics of the tests
# # testing approach
# # # Example screenshot


# # I)f the user clicks on the group they just made, is the delete button visible?
# # If user clicks siad delete button does a modal pop up fro confirmation? does this the remove the group from the home page?
# # if the user joins other groups, are those specific groups visible in the my_groups section?
# # If the user selects a group that they didn't make, does the join society button appear? if they are already a member does it show the leave button?

# # Does the calendar allow users to add the dates they are abailable?
# # if antoehr user adds dates afterwards, does this update to the new date availabilities?

# # If the users on the account is the creator, can they add an announcement that is visible for everyone?
# # If the user selects the account and presses delete, does their account get deleted from the fatabase?

# # if user is admin, does account page say they cant delete account and dfoes the groups page say they need to log in as not an admin
# # Can admins delete every society?
# # can admins add announcements to ANY sciety?

# # Does message page render?

