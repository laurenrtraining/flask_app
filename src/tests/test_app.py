import sys
import os
import pytest
from datetime import date, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Similar to what I needed to do in app.py, this line ensures the test file looks in the correct place for app

from app import app
from database.database import db, Staff, Societies, Staff_Societies, Date_Availability


# Using PyTest is very new to me, and I used the PyTest pages to help, therefore there are many comments to help me understand what is going on (Pytest, 2025).
# Unlike Jest, PyTest only works with backend code - this took me a while to understand that I didn't need to test button clicks, just the database functionality.

@pytest.fixture
# This client function simulates the database and prevents tests against real data
def client():
    app.config['TESTING'] = True # States that the app is in testing mode
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://:memory:' # Database is created purely im memory (SQLite, 2022)

    # Initialising client (Flask, 2024)
    with app.app_context():
        db.create_all()

        with app.test_client() as client:
            yield client

        db.session.remove()
        db.drop_all()
        # After running the tests, they are deleted from the database
        # This way they don't pollute the main db
    

### MAIN TESTS ###

# RENDER INDEX PAGE ON STARTUP
def test_render_index_when_logged_out(client):
    # GIVEN a logged-in staff user in the session
    # WHEN the index page is requested
    # THEN the response should be successful and contain the staff_username (Kennedy, 2023)
    response = client.get('/', follow_redirects=True)
    assert response.status_code == 200
    assert b'Guest' in response.data


### SIGN IN ###

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

    staff = Staff(staff_username='test_user', job_role='Non Admin', staff_email='test_user@staff.uk', password='testUser123')
    db.session.add(staff)
    db.session.commit()

    response = client.post('/sign_in.html', data={'staff_username':'test_user', 'password':'wrongPassword123'}, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data


### REGISTRATION ###

# TESTS THAT USER REGISTRATION SEARCHED DB BEFORE ALLOWING CREATION - ACCOUNT ALREADY EXISTS
def test_user_registration_if_existing(client):
    # Gets to the sign in page first
    response = client.get('/sign_in.html')
    assert response.status_code == 200

    staff = Staff(staff_username='test_user', job_role='Non Admin', staff_email='test_user@staff.uk', password='testUser123')
    db.session.add(staff)
    db.session.commit()

    # Confirm registration option is on the page
    assert b'Register' in response.data

    # Simulates clicking registration button
    response = client.get('/register.html')
    assert response.status_code == 200
    assert b'Registration Form' in response.data

    response = client.post('/register.html', data={'staff_username':'test_user1', 'job_role':'Non Admin', 'staff_email':'test_user@staff.uk', 'password':'testUser1234'}, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Email already registered. Please sign in.' in response.data


# TESTS THAT USER REGISTRATION SUCCESSFULLY ADDS TO DB
def test_user_registration_not_preexisting(client):
    # Gets to the sign in page first
    response = client.get('/sign_in.html')
    assert response.status_code == 200

    # Confirm registration option is on the page
    assert b'Register' in response.data

    # Simulates clicking registration button
    response = client.get('/register.html')
    assert response.status_code == 200
    assert b'Registration Form' in response.data

    response = client.post('/register.html', data={'staff_username':'test_user1', 'job_role':'Non Admin', 'staff_email':'test_user@staff.uk', 'password':'testUser1234'}, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Sign Out' in response.data



### CREATE SOCIETIES ###

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


### JOIN, LEAVE AND DELETE SOCIETIES ###

# TESTS THAT USERS CAN JOIN GROUPS
def test_join_group(client):
    creator = Staff(staff_username='creator', job_role='Non Admin', staff_email='creator@staff.uk', password='Creator123')
    db.session.add(creator)
    db.session.commit()

    # Logs in a user
    staff = Staff(staff_username='test_user', job_role='Non Admin', staff_email='test_user@staff.uk', password='testUser123')

    db.session.add(staff)
    db.session.commit()

    # Simulates staff session
    staff_id = staff.staff_id

    with client.session_transaction() as session:
        session['user_id'] = staff_id
        session['staff_username'] = staff.staff_username
        session['job_role'] = staff.job_role

    society = Societies(name='test_group', description='Test description', created_by=creator.staff_id)
    db.session.add(society)
    db.session.commit()

    response = client.post(f'/group/{society.society_id}/join', follow_redirects=True)
    assert response.status_code == 200
    assert b'Leave Society' in response.data  # Confirm they joined

    # Check the DB to verify the association
    membership = Staff_Societies.query.filter_by(staff_id=staff.staff_id, society_id=society.society_id).first()
    assert membership is not None


# TESTS THAT USERS CAN LEAVE GROUPS
def test_leave_group(client):
    creator = Staff(staff_username='creator', job_role='Non Admin', staff_email='creator@staff.uk', password='Creator123')
    db.session.add(creator)
    db.session.commit()

    # Logs in a user
    staff = Staff(staff_username='test_user', job_role='Non Admin', staff_email='test_user@staff.uk', password='testUser123')
    db.session.add(staff)
    db.session.commit()

    # Simulates staff session
    staff_id = staff.staff_id

    with client.session_transaction() as session:
        session['user_id'] = staff_id
        session['staff_username'] = staff.staff_username
        session['job_role'] = staff.job_role

    society = Societies(name='test_group', description='Test description', created_by=creator.staff_id)
    db.session.add(society)
    db.session.commit()
    
    response = client.post(f'/group/{society.society_id}/join', follow_redirects=True)
    assert response.status_code == 200
    assert b'Leave Society' in response.data  # Confirm they joined

    # Check the DB to verify they joined first
    membership = Staff_Societies.query.filter_by(staff_id=staff.staff_id, society_id=society.society_id).first()
    assert membership is not None

    # Needed to test they joined to compare to when they left
    response = client.post(f'/group/{society.society_id}/leave', follow_redirects=True)
    assert response.status_code == 200
    assert b'Join Society' in response.data  # Confirm they left

    # Check the DB to verify they left
    membership = Staff_Societies.query.filter_by(staff_id=staff.staff_id, society_id=society.society_id).first()
    assert membership is None


# TESTS THAT ADMIN CAN DELETE GROUPS
def test_delete_group_as_admin(client):
    creator = Staff(staff_username='creator', job_role='Non Admin', staff_email='creator@staff.uk', password='Creator123')
    db.session.add(creator)
    db.session.commit()

    # Logs in a user
    staff = Staff(staff_username='test_user', job_role='Admin', staff_email='test_user@staff.uk', password='testUser123')
    db.session.add(staff)
    db.session.commit()

    # Simulates staff session
    staff_id = staff.staff_id

    with client.session_transaction() as session:
        session['user_id'] = staff_id
        session['staff_username'] = staff.staff_username
        session['job_role'] = staff.job_role

    society = Societies(name='test_group', description='Test description', created_by=creator.staff_id)
    db.session.add(society)
    db.session.commit()
    
    response = client.post(f'/group/{society.society_id}/delete', follow_redirects=True)
    assert response.status_code == 200
    # Confirm deletion

    # Check the DB to verify society deletion
    society = Societies.query.filter_by(society_id=society.society_id).first()
    assert society is None

# TESTS THAT PAGE OWNER CAN DELETE GROUPS
def test_delete_group_non_admin(client):
    creator = Staff(staff_username='creator', job_role='Non Admin', staff_email='creator@staff.uk', password='Creator123')
    db.session.add(creator)
    db.session.commit()

    # Simulates staff session
    staff_id = creator.staff_id

    with client.session_transaction() as session:
        session['user_id'] = staff_id
        session['staff_username'] = creator.staff_username
        session['job_role'] = creator.job_role

    society = Societies(name='test_group', description='Test description', created_by=creator.staff_id)
    db.session.add(society)
    db.session.commit()

    response = client.post(f'/group/{society.society_id}/delete', follow_redirects=True)
    assert response.status_code == 200
    # Confirm deletion

    # Check the DB to verify society deletion
    society = Societies.query.filter_by(society_id=society.society_id).first()
    assert society is None



### TESTS TO EDIT GROUP DETAILS ###

# TESTS THAT ADMIN CAN EDIT GROUPS
def test_admin_edit_group(client):
    creator = Staff(staff_username='creator', job_role='Non Admin', staff_email='creator@staff.uk', password='Creator123')
    db.session.add(creator)
    db.session.commit()

    # Logs in a user
    staff = Staff(staff_username='test_user', job_role='Admin', staff_email='test_user@staff.uk', password='testUser123')
    db.session.add(staff)
    db.session.commit()

    # Simulates staff session
    staff_id = staff.staff_id

    with client.session_transaction() as session:
        session['user_id'] = staff_id
        session['staff_username'] = staff.staff_username
        session['job_role'] = staff.job_role

    society = Societies(name='test_group', description='Test description', created_by=creator.staff_id)
    db.session.add(society)
    db.session.commit()

    update_group = {'name':'edited_group','description':'testing edits'}
    
    response = client.post(f'/update_group/{society.society_id}', data=update_group, follow_redirects=True)
    assert response.status_code == 200
    # Confirm edit

    # Check the DB to verify society was edited successfully by ADMIN
    updated_society = db.session.get(Societies, society.society_id)
    assert updated_society.name == 'edited_group'
    assert updated_society.description == 'testing edits'

# TESTS THAT PAGE OWNER CAN EDIT GROUPS
def test_non_admin_edit_group(client):
    # Logs in a user
    staff = Staff(staff_username='test_user', job_role='Non Admin', staff_email='test_user@staff.uk', password='testUser123')
    db.session.add(staff)
    db.session.commit()

    # Simulates staff session
    staff_id = staff.staff_id

    with client.session_transaction() as session:
        session['user_id'] = staff_id
        session['staff_username'] = staff.staff_username
        session['job_role'] = staff.job_role

    society = Societies(name='test_group', description='Test description', created_by=staff.staff_id)
    db.session.add(society)
    db.session.commit()
    
    update_group = {'name':'edited_group','description':'testing edits'}
    
    response = client.post(f'/update_group/{society.society_id}', data=update_group, follow_redirects=True)
    assert response.status_code == 200
    # Confirm edit

    # Check the DB to verify society was edited successfully by PAGE OWNER
    updated_society = db.session.get(Societies, society.society_id)
    assert updated_society.name == 'edited_group'
    assert updated_society.description == 'testing edits'


### TESTING EDIT ACCOUNT ###
# BOTH NON ADMIN AND ADMIN HAVE THE SAME FORMAT SO ONLY TESTING ONE OF THEM ###

# TESTS THAT PAGE OWNER CAN EDIT GROUPS
def test_edit_account(client):
    # Logs in a user
    staff = Staff(staff_username='test_user', job_role='Non Admin', staff_email='test_user@staff.uk', password='testUser123')
    db.session.add(staff)
    db.session.commit()

    # Simulates staff session
    staff_id = staff.staff_id

    with client.session_transaction() as session:
        session['user_id'] = staff_id
        session['staff_username'] = staff.staff_username
        session['job_role'] = staff.job_role

    update_account = {'staff_username':'edited_username','staff_email':'edited_email@email.com', 'password':'', 'confirm_password':''}
    # Passwords not changing therefore blank

    response = client.post('/update_account', data=update_account, follow_redirects=True)
    assert response.status_code == 200
    # Confirm edit

    # Check the DB to verify account was edited successfully
    updated_account = db.session.get(Staff, staff.staff_id)
    assert updated_account.staff_username == 'edited_username'
    assert updated_account.staff_email == 'edited_email@email.com'


### TESTING DELETE ACCOUNT ###
### ONLY NON ADMINS CAN DELETE THEIR ACCOUNT, ADMINS CANNOT ###

# TESTS THAT USER CAN DELETE ACCOUNT
def test_delete_account(client):
    # Logs in a user
    staff = Staff(staff_username='test_user', job_role='Non Admin', staff_email='test_user@staff.uk', password='testUser123')
    db.session.add(staff)
    db.session.commit()

    # Simulates staff session
    staff_id = staff.staff_id

    with client.session_transaction() as session:
        session['user_id'] = staff_id
        session['staff_username'] = staff.staff_username
        session['job_role'] = staff.job_role

    response = client.post(f'/staff/{staff.staff_id}/delete', follow_redirects=True)
    assert response.status_code == 200
    # Confirm edit

    # Check the DB to verify account was edited successfully
    society = Staff.query.filter_by(staff_id=staff.staff_id).first()
    assert society is None


### TESTING CALENDAR AND ADMIN ANNOUNCEMENTS ###

# TESTS THAT USERS CAN ENTER DATES THEY ARE AVAILABLE INTO THE CALENDAR
def test_date_availabilty(client):
    # Logs in a user
    staff = Staff(staff_username='test_user', job_role='Non Admin', staff_email='test_user@staff.uk', password='testUser123')
    db.session.add(staff)
    db.session.commit()

    # Simulates staff session
    staff_id = staff.staff_id

    with client.session_transaction() as session:
        session['user_id'] = staff_id
        session['staff_username'] = staff.staff_username
        session['job_role'] = staff.job_role

    society = Societies(name='test_group', description='Test description', created_by=staff.staff_id)
    db.session.add(society)
    db.session.commit()

    # Simulate selecting two dates from the calendar from the day the test is run
    today = date.today()
    date_list = [(today + timedelta(days=i)).strftime('%a<br />%d-%m') for i in range(2)]
    new_dates = {'available_dates': date_list}

    response = client.post(f'/group/{staff.staff_id}', data=new_dates, follow_redirects=True)
    assert response.status_code == 200
    
   # Check the database for correct data added
    entries = Date_Availability.query.filter_by(staff_id=staff.staff_id, society_id=society.society_id).all()
    assert len(entries) == 2


# TESTS THAT ADMINS AND GROUP CREATORS CAN ADD AN ANNOUNCEMENT
def test_announcement(client):
    # Logs in a user
    staff = Staff(staff_username='test_user', job_role='Non Admin', staff_email='test_user@staff.uk', password='testUser123')
    db.session.add(staff)
    db.session.commit()

    # Simulates staff session
    staff_id = staff.staff_id

    with client.session_transaction() as session:
        session['user_id'] = staff_id
        session['staff_username'] = staff.staff_username
        session['job_role'] = staff.job_role

    society = Societies(name='test_group', description='Test description', created_by=staff.staff_id)
    db.session.add(society)
    db.session.commit()

    update_announcement = {'announcement':'This is an announcement'}

    response = client.post(f'/group/{society.society_id}/announcement', data=update_announcement, follow_redirects=True)
    assert response.status_code == 200
    # Confirm addition of announcement

    # Check the DB to verifythe announcement was added to the db
    updated_society = db.session.get(Societies, society.society_id)
    assert updated_society.announcement == 'This is an announcement'

# # Just do a couple of tests
# # Pics of the tests
# # testing approach
# # # Example screenshot