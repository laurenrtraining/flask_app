# Imports
from flask import Flask
from database import db, Staff  # adjust import to where your app and db live
import os


app = Flask(__name__, instance_relative_config=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'FLASK_DATABASE.db') 
# Specified file location outside of src
# Ensures database instance is created in the correct location

# Initialize db
db.init_app(app)

if __name__ == '__main__':
    os.makedirs(app.instance_path, exist_ok=True)
    with app.app_context():
        db.create_all()

# Only run once to initialise database