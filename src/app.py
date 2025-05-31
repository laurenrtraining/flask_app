from flask import Flask, render_template
import os
from database.database import db, Staff, Societies, Staff_Societies

instance_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'instance')) 
# needed so the instance isn't made within src

app = Flask(__name__, instance_relative_config=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'FLASK_DATABASE.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize db with app!
db.init_app(app)


#Creating homepage
# Add this route

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    os.makedirs(app.instance_path, exist_ok=True)
    app.run(debug=True)