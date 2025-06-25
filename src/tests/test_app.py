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

# TESTS THAT USER REGISTRATION SUCCESSFULLY HITS AND ADDS TO THE DATABASE
def test_user_registration(client):
    # Gets to the sign in page first
    response = client.get('/sign_in.html')
    assert response.status_code == 200

    # Confirm registration option is on the page
    assert b'Register' in response.data

    # Simulates clicking registration button
    response = client.get('/register.html')
    assert response.status_code == 200
    assert b'Registration Form' in response.data

    client.post('/register.html', data={'staff_username':'test_user', 'job_role':'test_role', 'staff_email':'test_user@staff.uk', 'password':'testUser123'}, follow_redirects=True)
    
    assert response.status_code == 200


# TESTS THAT USER CAN SIGN IN SUCCESSFULLY AND THAT THE DB SEARCH WORKS
def test_user_sign_in_success(client):
    # Gets to the sign in page first
    response = client.get('/sign_in.html')
    assert response.status_code == 200

    client.post('/sign_in.html', data={'staff_username':'test_user', 'password':'testUser123'}, follow_redirects=True)
    
    assert response.status_code == 200

# TESTS THAT VALIDATION WORKS BY IMPUTTING INCORRECT PASSWORD
def test_user_sign_in_fail(client):
    # Gets to the sign in page first
    response = client.get('/sign_in.html')
    assert response.status_code == 200

    client.post('/sign_in.html', data={'staff_username':'test_user', 'password':'wrongPassword123'}, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data


    # THIS TEST CURRENTLY ERRORS, TRYING TO WORK OUT WHY