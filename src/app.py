from flask import Flask, render_template, request, redirect, url_for, session
import os
from database.database import db, Staff, Societies, Staff_Societies, Date_Availability
from werkzeug.utils import secure_filename
from datetime import date, timedelta
from collections import defaultdict

instance_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'instance')) 
# needed so the instance isn't made within src

app = Flask(__name__, instance_path=instance_path, instance_relative_config=True, static_folder='static', template_folder='templates')

# In memory calendar store for demo
user_availability = {} 

# Ensures any uploaded images can be accessed when creating new groups
UPLOAD_FOLDER = 'static/group_images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

#  Configuring db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'FLASK_DATABASE.db') 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize db with app
db.init_app(app)

app.secret_key = os.urandom(24)
# Creating a secret key to run sessions for log ins and sign essential cookies on the website
# Random creation for added security

#Creating homepage
# Add the HTML webpage designs
@app.route('/')
def index():
    groups = Societies.query.all()
    return render_template('index.html', groups=groups)


@app.route('/sign_in.html', methods=['GET','POST'])
def sign_in():
    if request.method == 'POST':
        username = request.form.get('staff_username')
        password = request.form.get('password')

        user = Staff.query.filter_by(staff_username=username).first()

        if user and user.password == password:
            session['user_id'] = user.staff_username
            return redirect(url_for('index'))
        else:
            return render_template('sign_in.html', error="Invalid username or password")
        
    return render_template('sign_in.html')


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
            password=password  # Might need to store this hashed eventually
        )

        db.session.add(new_staff)
        db.session.commit()

        user = Staff.query.filter_by(staff_username=username).first()
        session['user_id'] = user.staff_username
        return redirect(url_for('index'))  
    
    return render_template('register.html')

# testing html page renders

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/about')
def about():
    return render_template('about.html')



# Creation of new groups
@app.route('/create-group')
def create_group():
    return render_template('create_group.html')

@app.route('/submit-group', methods=['POST'])
def submit_group():
    name = request.form.get('name')
    description = request.form.get('description')
    image = request.files.get('image_filename')
     # Get image and secure filename

    filename='default.png'

    if image and image.filename != '':
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.static_folder, 'group_images', filename))

    # Save to database
    new_group = Societies(
        name=name,
        description=description,
        created_by=session.get('user_id'),
        image_filename=filename,
    )

    db.session.add(new_group)
    db.session.commit()

    
    return redirect(url_for('index'))

@app.route('/group/<int:group_id>', methods=['GET', 'POST'])
def group_detail(group_id):
    group = Societies.query.get_or_404(group_id)
    today = date.today()
    date_list = [(today + timedelta(days=i)).strftime('%a<br />%d-%m')for i in range(31)]

    error = None  # default no error

    if request.method == 'POST':
        if 'user_id' not in session:
            error = "You must be logged in to submit availability."
        else:
            user_id = session['user_id']
            selected_dates = set(request.form.getlist('available_dates'))

             # Clear old availability entries for this user in this group
            Date_Availability.query.filter_by(user_id=user_id, group_id=group_id).delete()

            # Add new entries
            for date_str in selected_dates:
                new_entry = Date_Availability(
                    group_id=group_id,
                    user_id=user_id,
                    available_dates=date_str  # assuming it's stored as a string in your model
                )
                db.session.add(new_entry)

            db.session.commit()

    # Calculate common dates for display
    availability = defaultdict(set)
    entries = Date_Availability.query.filter_by(group_id=group_id).all()

    for entry in entries:
        availability[entry.user_id].add(entry.available_dates)

    if availability:
        common_dates = set.intersection(*availability.values())
    else:
        common_dates = set()

    return render_template(
        'society_template/group_detail.html',
        group=group,
        date_list=date_list,
        common_dates=common_dates,
        error=error
    )


# Checking if the database already exists

if __name__ == '__main__':
    os.makedirs(app.instance_path, exist_ok=True)
    with app.app_context():
        db.create_all()
    app.run(debug=True)