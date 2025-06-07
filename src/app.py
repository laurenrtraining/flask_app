from flask import Flask, render_template, request, redirect, url_for
import os
from database.database import db, Staff, Societies, Staff_Societies
from sqlalchemy import inspect

instance_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'instance')) 
# needed so the instance isn't made within src

app = Flask(__name__, instance_path=instance_path, instance_relative_config=True)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'FLASK_DATABASE.db') 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize db with app
db.init_app(app)

#Creating homepage
# Add the HTML webpage designs
@app.route('/')
def index():
    return render_template('index.html')
# testing html page renders

@app.route('/sign_in.html', methods=['GET','POST'])
def sign_in():
    if request.method == 'POST':
        username = request.form.get('staff_username')
        password = request.form.get('password')

        user = Staff.query.filter_by(staff_username=username).first()

        if user and user.password == password:
            return redirect(url_for('home'))  # or return a success message
        else:
            return render_template('sign_in.html', error="Invalid username or password")
        
    return render_template('sign_in.html')

# testing html page renders

@app.route('/register.html', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        username = request.form.get('staff_username')
        job_role = request.form.get('job_role')
        email = request.form.get('staff_email')
        password = request.form.get('password')


        # Optional: check if username or email already exists
        existing_user = Staff.query.filter_by(staff_email=email).first()
        if existing_user:
            return render_template('register.html', error="Email already registered. Please sign in.")

        # Add to DB
        new_staff = Staff(
            staff_username=username,
            job_role=job_role,
            staff_email=email,
            password=password  # Note: store hashed in real apps!
        )

        db.session.add(new_staff)
        db.session.commit()

        return redirect(url_for('home'))
    
    return render_template('register.html')

# testing html page renders

@app.route('/home.html')
def home():
    return render_template('home.html')  # Make sure home.html exists in your templates folder



# Checking if the database already exists

if __name__ == '__main__':
    os.makedirs(app.instance_path, exist_ok=True)
    with app.app_context():
        db.create_all()
    app.run(debug=True)