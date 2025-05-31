from flask_sqlalchemy import SQLAlchemy

# Creating database
db = SQLAlchemy()


# Defining models in the database

class Staff(db.Model):
    __tablename__ = "staff"

    staff_id = db.Column(db.Integer, primary_key=True)
    job_role = db.Column(db.String(100), nullable=False)
    staff_email = db.Column(db.String(200), nullable=False)
    staff_phone = db.Column(db.String(20), nullable=False)

class Societies(db.Model):
    __tablename__ = "societies"

    society_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    meeting_time = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('staff.staff_id'), nullable=False)

class Staff_Societies(db.Model):
    __tablename__ = "staff_societies"

    staff_societies_id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.staff_id'), nullable=False)
    society_id = db.Column(db.Integer, db.ForeignKey('societies.society_id'), nullable=False)
    date_joined = db.Column(db.String(200), nullable=False)
    society_role = db.Column(db.String(20), nullable=False)
