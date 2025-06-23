# Imports
from flask_sqlalchemy import SQLAlchemy

# Creating database
db = SQLAlchemy()


# Defining models in the database

class Staff(db.Model):
    __tablename__ = "staff"

    staff_id = db.Column(db.Integer, primary_key=True)
    staff_username = db.Column(db.String(200), nullable=False)
    job_role = db.Column(db.String(100), nullable=False)
    staff_email = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)

    # Staff defines all users of the website and every person who signs in

class Societies(db.Model):
    __tablename__ = "societies"

    society_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('staff.staff_id'), nullable=False)
    image_filename = db.Column(db.String(200), nullable=True)  # stores image filepath
    announcement = db.Column(db.String(200), nullable=True) 
    # announcement is always NULL when initiated, and is updated later on by group creator or webpage admin

    # Societies is all the groups that users can join and interact with


class Staff_Societies(db.Model):
    __tablename__ = "staff_societies"

    staff_societies_id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.staff_id'), nullable=False)
    society_id = db.Column(db.Integer, db.ForeignKey('societies.society_id'), nullable=False)
    date_joined = db.Column(db.String(200), nullable=False)

    # This group registers which staff members are members of which group

class Date_Availability(db.Model):
    __tablename__ = "date_availability"

    calendar_id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.staff_id'), nullable=False)
    society_id = db.Column(db.Integer, db.ForeignKey('societies.society_id'), nullable=False)
    available_dates = db.Column(db.PickleType, nullable=False)  # Stores list of dates

    # Lists all the dates users are available and which user submitted the change