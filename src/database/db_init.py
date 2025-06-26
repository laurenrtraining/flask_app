# Imports
from flask import Flask
import os
from datetime import date
import sqlalchemy
from sqlalchemy.dialects.sqlite import insert

print(sqlalchemy.__version__)
from database import db, Staff, Societies, Staff_Societies, Date_Availability


app = Flask(__name__, instance_relative_config=True)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    app.instance_path, "FLASK_DATABASE.db"
)

# Specified file location outside of src
# Ensures database instance is created in the correct location

# Initialize db
db.init_app(app)

if __name__ == "__main__":
    os.makedirs(app.instance_path, exist_ok=True)
    with app.app_context():
        db.create_all()

        # INSERT A SHIT TON OF TEST DATA

        staff_societies = [
            {
                "staff_societies_id": 1,
                "staff_id": 5,
                "society_id": 8,
                "date_joined": date(2025, 6, 26),
            },
            {
                "staff_societies_id": 2,
                "staff_id": 4,
                "society_id": 7,
                "date_joined": date(2025, 6, 26),
            },
            {
                "staff_societies_id": 3,
                "staff_id": 1,
                "society_id": 10,
                "date_joined": date(2025, 5, 15),
            },
            {
                "staff_societies_id": 4,
                "staff_id": 8,
                "society_id": 3,
                "date_joined": date(2025, 6, 10),
            },
            {
                "staff_societies_id": 5,
                "staff_id": 2,
                "society_id": 9,
                "date_joined": date(2025, 4, 22),
            },
            {
                "staff_societies_id": 6,
                "staff_id": 9,
                "society_id": 5,
                "date_joined": date(2025, 6, 26),
            },
            {
                "staff_societies_id": 7,
                "staff_id": 6,
                "society_id": 2,
                "date_joined": date(2025, 3, 30),
            },
            {
                "staff_societies_id": 8,
                "staff_id": 10,
                "society_id": 1,
                "date_joined": date(2025, 6, 1),
            },
            {
                "staff_societies_id": 9,
                "staff_id": 3,
                "society_id": 4,
                "date_joined": date(2025, 5, 4),
            },
            {
                "staff_societies_id": 10,
                "staff_id": 7,
                "society_id": 6,
                "date_joined": date(2025, 2, 18),
            },
        ]

        insert_staff_societies = insert(Staff_Societies).values(staff_societies)
        upsert_staff_societies = insert_staff_societies.on_conflict_do_update(
            index_elements=["staff_societies_id"],
            set_={
                "staff_id": insert_staff_societies.excluded.staff_id,
                "society_id": insert_staff_societies.excluded.society_id,
                "date_joined": insert_staff_societies.excluded.date_joined,
            },
        )
        db.session.execute(upsert_staff_societies)
        db.session.commit()

        staff = [
            {
                "staff_id": 1,
                "staff_username": "bluefalcon",
                "job_role": "Admin",
                "staff_email": "bluefalcon@gmail.com",
                "password": "Qf2_Ts3@gS!",
            },  # original already valid
            {
                "staff_id": 2,
                "staff_username": "starry_night",
                "job_role": "Non Admin",
                "staff_email": "starry_night@gmail.com",
                "password": "Wp9@Nv1qL",
            },
            {
                "staff_id": 3,
                "staff_username": "pixel_pioneer",
                "job_role": "Admin",
                "staff_email": "pixel_pioneer@gmail.com",
                "password": "Za7_Km4Rs",
            },
            {
                "staff_id": 4,
                "staff_username": "clever_fox",
                "job_role": "Non Admin",
                "staff_email": "clever_fox@gmail.com",
                "password": "Nx5_Qr8Df",
            },
            {
                "staff_id": 5,
                "staff_username": "lunar_tiger",
                "job_role": "Admin",
                "staff_email": "lunar_tiger@gmail.com",
                "password": "Lp2^Zv7Ht",
            },
            {
                "staff_id": 6,
                "staff_username": "quantum_leap",
                "job_role": "Non Admin",
                "staff_email": "quantum_leap@gmail.com",
                "password": "Gf9@Wx3Uk",
            },
            {
                "staff_id": 7,
                "staff_username": "digital_nomad",
                "job_role": "Admin",
                "staff_email": "digital_nomad@gmail.com",
                "password": "Vm6_Sz0Jr",
            },
            {
                "staff_id": 8,
                "staff_username": "neon_knight",
                "job_role": "Non Admin",
                "staff_email": "neon_knight@gmail.com",
                "password": "Rb1_Yx4Op",
            },
            {
                "staff_id": 9,
                "staff_username": "silent_raven",
                "job_role": "Admin",
                "staff_email": "silent_raven@gmail.com",
                "password": "Ht8_Uf5Qe",
            },
            {
                "staff_id": 10,
                "staff_username": "crimson_hawk",
                "job_role": "Non Admin",
                "staff_email": "crimson_hawk@gmail.com",
                "password": "Yz3^Lo2Nb",
            },
        ]
        insert_staff = insert(Staff).values(staff)
        upsert_staff = insert_staff.on_conflict_do_update(
            index_elements=["staff_id"],
            set_={
                "staff_id": insert_staff.excluded.staff_id,
                "staff_username": insert_staff.excluded.staff_username,
                "job_role": insert_staff.excluded.job_role,
                "staff_email": insert_staff.excluded.staff_email,
                "password": insert_staff.excluded.password,
            },
        )
        db.session.execute(upsert_staff)
        db.session.commit()

        societies = [
            {
                "society_id": 1,
                "name": "Climbing",
                "description": "V0s to V17s welcome for both top rope and bouldering!",
                "created_by": 3,
                "image_filename": "climbing.jpg",
                "announcement": "For our next meet up we will be going to the Castle, getting there for 10 with food afterwards!",
            },
            {
                "society_id": 2,
                "name": "Football",
                "description": "Join us to play friendly and competitive football matches.",
                "created_by": 5,
                "image_filename": "football.jpg",
                "announcement": None,
            },
            {
                "society_id": 3,
                "name": "Tennis",
                "description": "All skill levels welcome for tennis practice and matches.",
                "created_by": 6,
                "image_filename": "tennis.jpg",
                "announcement": "Tournament sign-ups open next week, don’t miss out!",
            },
            {
                "society_id": 4,
                "name": "Swimming",
                "description": "Join us for swim training and fun competitions.",
                "created_by": 7,
                "image_filename": "swimming.jpg",
                "announcement": None,
            },
            {
                "society_id": 5,
                "name": "Cycling",
                "description": "Group rides and endurance training for all levels.",
                "created_by": 1,
                "image_filename": "cycling.jpg",
                "announcement": "Sunday morning ride canceled due to weather.",
            },
            {
                "society_id": 6,
                "name": "Volleyball",
                "description": "Indoor and beach volleyball sessions every week.",
                "created_by": 4,
                "image_filename": "volleyball.jpg",
                "announcement": None,
            },
            {
                "society_id": 7,
                "name": "Rugby",
                "description": "Competitive and social rugby games.",
                "created_by": 8,
                "image_filename": "rugby.jpg",
                "announcement": None,
            },
            {
                "society_id": 8,
                "name": "Gymnastics",
                "description": "Training sessions for all gymnastics disciplines.",
                "created_by": 9,
                "image_filename": "gymnastics.jpg",
                "announcement": "Next competition is scheduled for July 15th.",
            },
            {
                "society_id": 10,
                "name": "Kayaking",
                "description": "Explore rivers and lakes with guided kayaking trips for beginners and experts alike.",
                "created_by": 7,
                "image_filename": "kayaking.jpg",
                "announcement": None,
            },
            {
                "society_id": 10,
                "name": "Badminton",
                "description": "Casual and competitive badminton matches weekly.",
                "created_by": 2,
                "image_filename": "badminton.jpg",
                "announcement": None,
            },
        ]

        insert_societies = insert(Societies).values(societies)
        upsert_societies = insert_societies.on_conflict_do_update(
            index_elements=["society_id"],
            set_={
                "society_id": insert_societies.excluded.society_id,
                "name": insert_societies.excluded.name,
                "description": insert_societies.excluded.description,
                "created_by": insert_societies.excluded.created_by,
                "image_filename": insert_societies.excluded.image_filename,
                "announcement": insert_societies.excluded.announcement,
            },
        )
        db.session.execute(upsert_societies)
        db.session.commit()

        date_availability = [
            {
                "calendar_id": 1,
                "staff_id": 5,
                "society_id": 8,
                "calendar_dates": date(2025, 4, 22),
            },
            {
                "calendar_id": 2,
                "staff_id": 3,
                "society_id": 8,
                "calendar_dates": date(2025, 6, 27),
            },
            {
                "calendar_id": 3,
                "staff_id": 3,
                "society_id": 8,
                "calendar_dates": date(2025, 6, 30),
            },
            {
                "calendar_id": 4,
                "staff_id": 7,
                "society_id": 5,
                "calendar_dates": date(2025, 7, 1),
            },
            {
                "calendar_id": 5,
                "staff_id": 1,
                "society_id": 4,
                "calendar_dates": date(2025, 7, 5),
            },
            {
                "calendar_id": 6,
                "staff_id": 2,
                "society_id": 3,
                "calendar_dates": date(2025, 7, 10),
            },
            {
                "calendar_id": 7,
                "staff_id": 9,
                "society_id": 6,
                "calendar_dates": date(2025, 7, 12),
            },
            {
                "calendar_id": 8,
                "staff_id": 5,
                "society_id": 8,
                "calendar_dates": date(2025, 7, 15),
            },
            {
                "calendar_id": 9,
                "staff_id": 4,
                "society_id": 9,
                "calendar_dates": date(2025, 7, 20),
            },
            {
                "calendar_id": 10,
                "staff_id": 7,
                "society_id": 5,
                "calendar_dates": date(2025, 7, 22),
            },
            {
                "calendar_id": 11,
                "staff_id": 6,
                "society_id": 7,
                "calendar_dates": date(2025, 7, 25),
            },
        ]

        insert_date_availability = insert(Date_Availability).values(date_availability)
        upsert_date_availability = insert_date_availability.on_conflict_do_update(
            index_elements=["calendar_id"],
            set_={
                "calendar_id": insert_date_availability.excluded.calendar_id,
                "staff_id": insert_date_availability.excluded.staff_id,
                "society_id": insert_date_availability.excluded.society_id,
                "calendar_dates": insert_date_availability.excluded.calendar_dates,
            },
        )
        db.session.execute(upsert_date_availability)
        db.session.commit()


# Only run once to initialise database
