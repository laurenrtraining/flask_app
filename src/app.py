# Imports
from flask import Flask, render_template, request, redirect, url_for, session, abort
import os
from database.database import db, Staff, Societies, Staff_Societies, Date_Availability
from werkzeug.utils import secure_filename
from datetime import date, timedelta
from collections import defaultdict

instance_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'instance')) 
# I needed to specify the route so the database isn't made in the wrong file

app = Flask(__name__, instance_path=instance_path, instance_relative_config=True, static_folder='static', template_folder='templates')
# All HTML files are stored in 'templates', images are stored in 'static'

# Ensures any uploaded images can be accessed when creating new groups
UPLOAD_FOLDER = 'static/group_images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

#  Configuring db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'FLASK_DATABASE.db') 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize db with app - ensures it already exists
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
    job_role = session.get('job_role')
    return render_template('index.html', groups=groups, job_role=job_role)
# Shows 'create group' if users are signed in and displays all groups in existence

# Render sign in page
@app.route('/sign_in.html', methods=['GET','POST'])
def sign_in():
    if request.method == 'POST':
        username = request.form.get('staff_username')
        password = request.form.get('password')

        user = Staff.query.filter_by(staff_username=username).first()
        # Checks that the user exists in the database

        if user and user.password == password:
            session['user_id'] = user.staff_id
            session['staff_username'] = user.staff_username
            session['job_role'] = user.job_role
            return redirect(url_for('index')) 
            # these call route through the name of the funtion, not the html route - makes the code tidier
        else:
            # If username or password is incorrect or doesn't exist it throws an error
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
        # Gathers the data from the form to add data to database

        # Checks if user already exists
        existing_user = Staff.query.filter_by(staff_email=email).first()
        if existing_user:
            return render_template('register.html', error="Email already registered. Please sign in.")

        # Add to DB
        new_staff = Staff(
            staff_username=username,
            job_role=job_role,
            staff_email=email,
            password=password  # Eventually might add this as hashes for privacy against admins seeing everyones
        )

        db.session.add(new_staff)
        db.session.commit()

        user = Staff.query.filter_by(staff_username=username).first()
        # Checks that the user exists now they have been added to database
        session['user_id'] = user.staff_id
        session['staff_username'] = user.staff_username
        session['job_role'] = user.job_role
        return redirect(url_for('index'))  
        # Logs the user in successfully
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    # Clears the session so no user data is accidentally kept
    return redirect(url_for('index'))
    # Back to homepage


### RENDERING ACCOUNT PAGE AND SETTINGS ###


@app.route('/my_account')
def my_account():
    user_id = session.get('user_id')
    staff_username = session.get('staff_username')
    job_role = session.get('job_role')
    staff = Staff.query.get(user_id)

    return render_template('my_account.html', staff=staff, staff_username=staff_username, job_role=job_role)
    # Account page is rendered

@app.route('/staff/<int:staff_id>/delete', methods=['POST'])
def delete_account(staff_id):
    staff = Staff.query.get_or_404(staff_id)

    # If this member of staff is a part of any groups this ensures that they are removed from the group too
    membership = Staff_Societies.query.filter_by(society_id=staff_id).first()
    if membership:
        db.session.delete(membership)
        # Deletes the users memberships and removes them from the groups
        db.session.commit()

    db.session.delete(staff)
    # Deletes user account
    db.session.commit()
    session.clear()
    return redirect(url_for('index'))  # Return to homepage



### RENDERING NAVBAR LINKS ###

@app.route('/about')
def about():
    return render_template('about.html')
    # Shows the about page

@app.route('/messages')
def messages():
    return render_template('messages.html')
    # Shows the about page

@app.route('/my_groups')
def my_groups():
    user_id = session.get('user_id')
    job_role = session.get('job_role')
    # If the user is not logged in it shows no groups
    if not user_id:
        return render_template('my_groups.html', user_id=None, groups=[])

    memberships = Staff_Societies.query.filter_by(staff_id=user_id).all()
    # Checks Staff_Societies db for societies where the current logged in staff session matcheS
    society_ids = [x.society_id for x in memberships]
    # Loops through Staff_Societies and finds the Society_id for each of them

    user_societies = Societies.query.filter(Societies.society_id.in_(society_ids)).all()
    # Groups all the society ids together to be called

    return render_template('my_groups.html', user_id=user_id, job_role=job_role, groups=user_societies)
    # Calls all existing societies that the user logged in is a member of and displays them


### CREATING NEW GROUPS/SOCIETIES ###

# Creation of new groups
@app.route('/create-group')
def create_group():
    return render_template('create_group.html')
    # Create group popup page

# Saves new group to database and renders it on the homepage
@app.route('/submit-group', methods=['POST'])
def submit_group():
    name = request.form.get('name')
    description = request.form.get('description')
    image = request.files.get('image_filename')
     # Get image and secure filename

    filename='default.png'
    # This is the default image - stored in 'static/group_images'

    if image and image.filename != '':
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.static_folder, 'group_images', filename))
        # Saves to database regardless of if there is an image found or not

    # Save to database
    new_group = Societies(
        name=name,
        description=description,
        created_by=session.get('user_id'),
        image_filename=filename,
    )

    db.session.add(new_group) 
    # Add group to Societies database
    db.session.commit()
    return redirect(url_for('index'))
    # Return to homepage


### CODE BASE FOR ALL NEW SOCIETIES THAT ARE MADE - MADE GENERIC FOR ALL SOCIETIES ###

@app.route('/group/<int:group_id>', methods=['GET', 'POST'])
def group_detail(group_id):
    group = Societies.query.get_or_404(group_id)
    user_id = session.get('user_id')
    job_role = session.get('job_role')
    # Checks user exists, that the user_id and whether the job_role is admin or not

    is_admin = (job_role == 'Admin')
    is_creator = (user_id == group.created_by) if user_id else False
    can_delete = (is_creator or is_admin)
    # checks if the society was created by the user currently logged in

    today = date.today() 
    # From today, the calendar will show a consecutive month
    date_list = [(today + timedelta(days=i)).strftime('%a<br />%d-%m')for i in range(31)] 
    # In the form (abbreviated day, date, month) and spans 31 days (1 month)

    error = None  # default no error

    # Is user already a member of this group?
    is_member = False

    if user_id:
        is_member = Staff_Societies.query.filter_by(staff_id=user_id, society_id=group_id).first()
        # Checks if the user id is already a member
    
    if request.method == 'POST':
        if 'user_id' not in session:
            # If the user isn't logged in this error will be thrown
            error = "You must be logged in to submit availability."
        else:
            selected_dates = set(request.form.getlist('available_dates'))
            # Show available dates

             # Clear old availability entries for this user ready for replacement
            Date_Availability.query.filter_by(staff_id=user_id, society_id=group_id).delete()

            # Add new entries
            for date_str in selected_dates:
                new_entry = Date_Availability(
                    society_id=group_id,
                    staff_id=user_id,
                    available_dates=date_str  # assuming it's stored as a string in your model
                )
                db.session.add(new_entry)
                # Add date availabilities to database

            db.session.commit()

    # Calculate common dates for display
    availability = defaultdict(set)
    entries = Date_Availability.query.filter_by(society_id=group_id).all()
    # Finds all date entries for the selected society

    for entry in entries:
        availability[entry.staff_id].add(entry.available_dates)
        # Loops through every entry one at a time

    if availability:
        common_dates = set.intersection(*availability.values())
        # Searches for the dates that every user has in common
    else:
        common_dates = set()

    return render_template(
        'society_template/group_detail.html',
        group = Societies.query.get_or_404(group_id),
        user_id=session.get('user_id'),
        is_member=is_member,
        is_creator=is_creator,
        is_admin=is_admin,
        job_role=job_role,
        can_delete=can_delete,
        date_list=date_list,
        common_dates=common_dates,
        error=error,
    )
    # Everything that needs rendering for this page to work


### DELETING GROUPS FROM THE DATABASE ###

@app.route('/group/<int:group_id>/delete', methods=['POST'])
def delete_group(group_id):
    group = Societies.query.get_or_404(group_id)
    user_id = session.get('user_id')
    job_role = session.get('job_role')
    is_admin = (job_role == 'Admin')
    is_creator = (user_id == group.created_by) if user_id else False
    can_delete = (is_creator or is_admin)

    if not can_delete:
        abort(403)  # Forbidden

    membership = Staff_Societies.query.filter_by(society_id=group_id).first()
    if membership:
        db.session.delete(membership)
        db.session.commit()
    # Deletes the members from this society before the actual society is deleted
    # This prevents issues like the users being members of a group that doesn't exist
    # A previous error found that without this fix, users were automatically added to the next group to be made as it adopted the old groups ID

    db.session.delete(group)
    db.session.commit()
    return redirect(url_for('index'))  # Return to homepage


### ADDING AN ANNOUNCEMENT TO GROUP PAGE AND DATABASE ###

@app.route('/group/<int:group_id>/announcement', methods=['POST'])
def announcement(group_id):
    group = Societies.query.get_or_404(group_id)
    user_id = session.get('user_id')
    job_role = session.get('job_role')
    is_admin = (job_role == 'Admin')
    is_creator = (user_id == group.created_by) if user_id else False
    can_delete = (is_creator or is_admin)

    if not can_delete:
        abort(403)  # Forbidden

    # Save to database
    new_announcement = request.form.get('announcement','').strip()
    # checks the database and overwrites what is there

    if new_announcement:
        group.announcement = new_announcement
        db.session.commit()
        # Overwrites new announcement and adds it to the Societies database where the 'NULL' used to be

    return redirect(url_for('group_detail',
        group_id=group_id,
        is_creator=is_creator,
        is_admin=is_admin,
        job_role=job_role,
        can_delete=can_delete,
        new_announcement=group.announcement)) 

# Adds to database and then renders on the page by calling from the database



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
    # Add member to
    db.session.commit()
    return redirect(url_for('group_detail', group_id=group_id))

# Leave group
@app.route('/group/<int:group_id>/leave', methods=['POST'])
def leave_group(group_id):
    user_id = session.get('user_id')
    
    # If user is not logged in
    if not user_id:
        return redirect(url_for('group_detail', group_id=group_id), error="Please log in to leave this society")

    membership = Staff_Societies.query.filter_by(staff_id=user_id, society_id=group_id).first()
    # Searched database for membership existence
    if membership:
        db.session.delete(membership)
        # Remove member from the database
        db.session.commit()

    return redirect(url_for('group_detail', group_id=group_id))



# RUNS THE APPLICATION AND CHECKS DATABASE EXISTENCE #
if __name__ == '__main__':
    os.makedirs(app.instance_path, exist_ok=True)
    with app.app_context():
        db.create_all()
    app.run(debug=True)