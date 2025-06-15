from flask import Flask, render_template, request, redirect, url_for, session, abort
import os
from database.database import db, Staff, Societies, Staff_Societies, Date_Availability
from werkzeug.utils import secure_filename
from datetime import date, timedelta
from collections import defaultdict

instance_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'instance')) 
# I needed to specify the route so the database isn't made in the wrong file

app = Flask(__name__, instance_path=instance_path, instance_relative_config=True, static_folder='static', template_folder='templates')

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
# Creating a secret key to run login sessions
# Random creation for added security


### App.routes for rendering all pages ###
### REGISTRSTION AND SIGN IN ###

# Render homepage
@app.route('/')
def index():
    groups = Societies.query.all()
    staff_username = session.get('staff_username')
    return render_template('index.html', groups=groups, staff_username=staff_username)

# Render sign in page
@app.route('/sign_in.html', methods=['GET','POST'])
def sign_in():
    if request.method == 'POST':
        username = request.form.get('staff_username')
        password = request.form.get('password')

        user = Staff.query.filter_by(staff_username=username).first()

        if user and user.password == password:
            session['user_id'] = user.staff_id
            session['staff_username'] = user.staff_username
            return redirect(url_for('index')) # these call route through the name of the funtion, not the html route - makes the code tidier
        else:
            return render_template('sign_in.html', error="Invalid username or password")
        
    return render_template('sign_in.html')

# Render regsistration page
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
        session['user_id'] = user.staff_id
        session['staff_username'] = user.staff_username
        return redirect(url_for('index'))  
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


### RENDERING ACCOUNT PAGE AND SETTINGS ###


@app.route('/my_account')
def my_account():
    user_id = session.get('user_id')
    staff_username = session.get('staff_username')
    staff = Staff.query.get(user_id)

    return render_template('my_account.html', staff=staff, staff_username=staff_username)

@app.route('/staff/<int:staff_id>/delete', methods=['POST'])
def delete_account(staff_id):
    staff = Staff.query.get_or_404(staff_id)
    db.session.delete(staff)
    db.session.commit()
    session.clear()
    return redirect(url_for('index'))  # Return to homepage

### RENDERING NAVBAR LINKS ###

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/my_groups')
def my_groups():
    user_id = session.get('user_id')
    if not user_id:
        return render_template('my_groups.html', user_id=None, groups=[])

    memberships = Staff_Societies.query.filter_by(staff_id=user_id).all()
    # checks Staff_Societies db for where the current logged in staff matcheS
    society_ids = [x.society_id for x in memberships]
    # Loops through Staff_Societies and finds the Society_id for each of them

    user_societies = Societies.query.filter(Societies.society_id.in_(society_ids)).all()
    # groups all the society ids together to be called

    return render_template('my_groups.html', user_id=user_id, groups=user_societies)



### CREATING NEW GROUPS/SOCIETIES ###

# Creation of new groups
@app.route('/create-group')
def create_group():
    return render_template('create_group.html')

# Saves new group to database and renders it on the homepage
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


### CODE BASE FOR ALL NEW SOCIETIES THAT ARE MADE ###

@app.route('/group/<int:group_id>', methods=['GET', 'POST'])
def group_detail(group_id):
    group = Societies.query.get_or_404(group_id)
    user_id = session.get('user_id')
    
    is_creator = (user_id == group.created_by) if user_id else False
    # checks if the society was created by the user currently logged in

    today = date.today() 
    #From today, the calendar will show a consecutive month
    date_list = [(today + timedelta(days=i)).strftime('%a<br />%d-%m')for i in range(31)] 
    # In the form (abbreviated day, date, month)

    error = None  # default no error

    # Is user already a member of this group?
    is_member = False # Pre-set

    if user_id:
        is_member = Staff_Societies.query.filter_by(staff_id=user_id, society_id=group_id).first()
    
    if request.method == 'POST':
        if 'user_id' not in session:
            # If the user isn't logged in this error will be thrown
            error = "You must be logged in to submit availability."
        else:
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
        is_member=is_member,
        is_creator=is_creator,
        date_list=date_list,
        common_dates=common_dates,
        error=error
    )


### DELETING GROUPS FROM THE DATABASE ###

@app.route('/group/<int:group_id>/delete', methods=['POST'])
def delete_group(group_id):
    group = Societies.query.get_or_404(group_id)
    user_id = session.get('user_id')

    if user_id != group.created_by:
        abort(403)  # Forbidden

    membership = Staff_Societies.query.filter_by(society_id=group_id).first()
    if membership:
        db.session.delete(membership)
        db.session.commit()

    db.session.delete(group)
    db.session.commit()
    return redirect(url_for('index'))  # Return to homepage


### JOIN AND LEAVE GROUPS ###

# Join Group
@app.route('/group/<int:group_id>/join', methods=['POST'])
def join_group(group_id):
    user_id = session.get('user_id')

    # If user is not logged in
    if not user_id:
        return redirect(url_for('group_detail', group_id=group_id), error="Please log in to join this society")

    # Add new member
    member = Staff_Societies(
        staff_id=user_id,
        society_id=group_id,
        date_joined=date.today()
    )
    db.session.add(member)
    db.session.commit()
    return redirect(url_for('group_detail', group_id=group_id))

# Leave group
@app.route('/group/<int:group_id>/leave', methods=['POST'])
def leave_group(group_id):
    user_id = session.get('user_id')
    
    if not user_id:
        return redirect(url_for('group_detail', group_id=group_id), error="Please log in to leave this society")

    membership = Staff_Societies.query.filter_by(staff_id=user_id, society_id=group_id).first()
    if membership:
        db.session.delete(membership)
        db.session.commit()

    return redirect(url_for('group_detail', group_id=group_id))



# RUNS THE APPLICATION AND CHECKS DATABASE EXISTENCE #
if __name__ == '__main__':
    os.makedirs(app.instance_path, exist_ok=True)
    with app.app_context():
        db.create_all()
    app.run(debug=True)