from flask import Flask
from database import db, Staff  # adjust import to where your app and db live
import os


app = Flask(__name__, instance_relative_config=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'FLASK_DATABASE.db') 
# Specified file location outside of src
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize db with app
db.init_app(app)

if __name__ == '__main__':
    os.makedirs(app.instance_path, exist_ok=True)
    with app.app_context():
        db.create_all()
        print("Database tables created!")

        # Check if admin user exists
        admin = Staff.query.filter_by(staff_username='admin').first()
        if not admin:
            admin_user = Staff(
            staff_username='admin',
            job_role='admin',
            staff_email='admin@staff.uk',
            password='admin123'
        )
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created!")
        else:
            print("Admin user already exists.")



# Only run once to initialise database