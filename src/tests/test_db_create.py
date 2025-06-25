import sys
import os

# Using PyTest is very new to me, and I used these pages to help (Pytest, 2025)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Similar to what I needed to do in app.py, I needed this line to ensure the test file was looking in the correct place for the file

import pytest
from app import app
from database.database import db, Staff, Societies, Staff_Societies,Date_Availability

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()

        staff1 = Staff(username='admin_user')
        staff2 = Staff(username='regular_user')

        society1 = Societies(name='Chess Club')
        society2 = Societies(name='Drama Society')

        db.session.add_all([staff1, staff2, society1, society2])
        db.session.commit()

    return client

       