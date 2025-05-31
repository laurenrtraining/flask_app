from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Create Flask app
app = Flask(__name__)

# Configure database URI — use SQLite database file
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///NEW_DATABASE_FLASK.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define your model outside the function - there are the tables in the database
class Staff(db.Model):
    staff_id = db.Column(db.Integer, primary_key=True)
    job_role = db.Column(db.String(100), nullable=False)
    staff_email = db.Column(db.String(200), nullable=False)
    staff_phone = db.Column(db.string(20), nullable=False)

class Societies(db.Model):
    society_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    meeting = db.Column(db.string(20), nullable=False)

class Staff(db.Model):
    staff_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    staff_email = db.Column(db.String(200), nullable=False)
    staff_phone = db.Column(db.string(20), nullable=False)

# # Create tables
# def create_tables():
#     commands = (
#         name VARCHAR (255) NOT NULL, 
#         description VARCHAR (255) NOT NULL, 
#         meeting_time VARCHAR (255) NOT NULL, 
#         location VARCHAR (255) NOT NULL,
#         FOREIGN KEY (created_by) REFERENCES staff(staff_id)
#         )
#         """,
#         """
#         CREATE TABLE staff_societies (
#         staff_societies_id SERIAL PRIMARY KEY,
#         staff_id INTEGER NOT NULL,
#         society_id INTEGER NOT NULL, 
#         date_joined VARCHAR (255) NOT NULL,
#         society_role VARCHAR (255) NOT NULL,
#         FOREIGN KEY (staff_id) REFERENCES staff(staff_id),
#         FOREIGN KEY (society_id) REFERENCES societies(society_id)
#         )
#         """)
#     db.create_all()

# # Add new item
# def add_item():



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database table created!")
