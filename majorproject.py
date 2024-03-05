from flask import Flask, render_template, request, session, redirect
from mongoproject3 import MongoDBHelper  # Assuming you have a separate module for MongoDB operations
import datetime
import hashlib
from datetime import datetime

web_app = Flask('Hospital')
web_app.secret_key = 'your_secret_key'  # Moved secret key initialization here


@web_app.route("/")
def login():
    return render_template("index.html")


@web_app.route("/register")
def register():
    return render_template("register.html")

@web_app.route("/register-patient", methods=['POST'])
def register_patient():
    email = request.form['email']

    db = MongoDBHelper(collection="Hospital")
    existing_patient = db.fetch_one({'email': email})

    if existing_patient:
        return render_template('error.html', message=f'{email} already registered')

    patient_data = {
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'contact': request.form['contact'],
        'email': request.form['email'],
        'gender': request.form['gender'],
        'password': hashlib.sha256(request.form['password'].encode('utf-8')).hexdigest(),
        'createdOn': datetime.datetime.today()
    }

    db.insert(patient_data)

    session['patient_id'] = str(patient_data['_id'])
    session['patient_first_name'] = patient_data['first_name']
    session['patient_email'] = patient_data['email']
    session['patient_contact'] = patient_data['contact']

    return render_template('patientDashboard.html')


@web_app.route("/login-patient", methods=['POST'])
def login_patient():
    login_data = {
        'email': request.form['email'],
        'password': hashlib.sha256(request.form['password'].encode('utf-8')).hexdigest(),
    }

    db = MongoDBHelper(collection="Hospital")
    documents = list(db.fetch(login_data))
    if len(documents) == 1:
        session['id'] = str(documents[0]['_id'])
        session['email'] = documents[0]['email']
        session['patient_id'] = str(documents[0]['_id'])
        session['first_name'] = documents[0]['first_name']
        return render_template('patientDashboard.html')
    else:
        return render_template('error.html', message="Incorrect Email And Password ")


@web_app.route("/admin-login", methods=['POST'])
def admin_login():
    entered_email = request.form.get('email')
    entered_password = request.form.get('password')

    admin_email = "admin@example.com"
    admin_password = "admin123"

    if entered_email == admin_email and entered_password == admin_password:
        return render_template('admin-home.html')
    else:
        return render_template('error.html', message="Incorrect Email or Password ")


@web_app.route("/register-doctor", methods=['POST'])
def register_doctor():
    doctor_data = {
        'name': request.form['name'],
        'email': request.form['email'],
        'gender': request.form['gender'],
        'specialization': request.form['specialization'],
        'fee': request.form['fee'],
        'password': hashlib.sha256(request.form['password'].encode('utf-8')).hexdigest()
    }

    db = MongoDBHelper(collection="doctor-hospital")
    db.insert(doctor_data)

    return "Doctor registered successfully!"


@web_app.route("/login-doctor", methods=['POST'])
def login_doctor():
    login_doctor_data = {
        'email': request.form['email'],
        'password': hashlib.sha256(request.form['password'].encode('utf-8')).hexdigest(),
    }

    db = MongoDBHelper(collection="doctor-hospital")
    documents = list(db.fetch(login_doctor_data))
    if len(documents) == 1:
        session['email'] = documents[0]['email']
        return "doctor login successful"
    else:
        return render_template('error.html', message="Incorrect Email And Password ")

@web_app.route("/doctors")
def doctors():
    specialization = request.args.get('specialization')
    if specialization:
        db = MongoDBHelper(collection="doctor-hospital")
        doctors = db.fetch({'specialization': specialization})
        current_date = datetime.now().strftime("%Y-%m-%d")  # Get current date in the format YYYY-MM-DD
        return render_template("doctor.html", doctors=doctors, current_date=current_date)
    else:
        # Handle case when no specialization is provided
        return "No specialization provided"



@web_app.route("/book", methods=['POST'])
def book_appointment():
    if request.method == 'POST':
        doctor_email = request.form['doctor_email']
        appointment_date = request.form['appointment_date']
        appointment_time = request.form['appointment_time']

        appointment_datetime = datetime.strptime(f"{appointment_date} {appointment_time}", "%Y-%m-%d %H:%M").strftime(
            "%Y-%m-%d %I:%M %p")

        if datetime.strptime(appointment_datetime, "%Y-%m-%d %I:%M %p") < datetime.now():
            return "Please select a future date and time for the appointment."

        appointment_data = {
            'doctor_email': doctor_email,
            'appointment_datetime': appointment_datetime,
        }

        db = MongoDBHelper(collection="doctor-appointment")
        db.insert(appointment_data)

        return "Appointment booked successfully!"
    else:
        return "Invalid request method"


if __name__ == "__main__":
    web_app.run(port=5000)
