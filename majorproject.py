from flask import Flask, render_template, session, redirect
from mongoproject3 import MongoDBHelper
import datetime
import hashlib
from datetime import datetime
from flask import request
from bson import ObjectId



web_app = Flask('Hospital')
web_app.secret_key = 'your_secret_key'


@web_app.route("/")
def login_all():
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
        'createdOn': datetime.now()
    }

    db.insert(patient_data)

    session['patient_id'] = str(patient_data['_id'])
    session['patient_first_name'] = patient_data['first_name']
    session['patient_email'] = patient_data['email']
    session['patient_contact'] = patient_data['contact']

    return render_template('patientDashboard.html')


@web_app.route("/login", methods=['POST'])
def login():
    email = request.form['email']
    password_hash = hashlib.sha256(request.form['password'].encode('utf-8')).hexdigest()
    password = request.form['password']

    hospital_db = MongoDBHelper(collection="Hospital")
    hospital_documents = list(hospital_db.fetch({'email': email, 'password': password_hash}))
    if len(hospital_documents) == 1:
        session['id'] = str(hospital_documents[0]['_id'])
        session['email'] = hospital_documents[0]['email']
        session['patient_id'] = str(hospital_documents[0]['_id'])
        session['first_name'] = hospital_documents[0]['first_name']
        print(session)
        return render_template('patientDashboard.html')

    doctor_db = MongoDBHelper(collection="doctor-hospital")
    doctor_documents = list(doctor_db.fetch({'email': email, 'password': password}))
    if len(doctor_documents) == 1:
        session['doctor_email'] = doctor_documents[0]['email']  # Store doctor's email in session
        print(session)
        return render_template('doctor-home.html')

    admin_email = "admin@example.com"
    admin_password = "admin123"
    if email == admin_email and password == admin_password:
        return render_template('admin-home.html')

    return render_template('error.html', message="Incorrect Email or Password ")


@web_app.route("/register-doctor", methods=['POST'])
def register_doctor():
    doctor_data = {
        'doctor_name': request.form['doctor_name'],
        'email': request.form['email'],
        'gender': request.form['gender'],
        'specialization': request.form['specialization'],
        'fee': request.form['fee'],
        'password': request.form['password']
    }

    db = MongoDBHelper(collection="doctor-hospital")
    db.insert(doctor_data)

    return "Doctor registered successfully!"


@web_app.route("/doctors")
def doctors():
    specialization = request.args.get('specialization')
    if specialization:
        db = MongoDBHelper(collection="doctor-hospital")
        doctors = db.fetch({'specialization': specialization})
        current_date = datetime.now().strftime("%Y-%m-%d")
        return render_template("doctor.html", doctors=doctors, current_date=current_date)
    else:
        return "No specialization provided"


@web_app.route("/book", methods=['POST'])
def book_appointment():
    if request.method == 'POST':
        doctor_name = request.form['doctor_name']
        doctor_email = request.form['doctor_email']
        appointment_date = request.form['appointment_date']
        appointment_time = request.form['appointment_time']

        patient_name = session.get('first_name')
        patient_email = session.get('email')

        appointment_datetime = datetime.strptime(f"{appointment_date} {appointment_time}", "%Y-%m-%d %I:%M %p")

        if appointment_datetime < datetime.now():
            return "Please select a future date and time for the appointment."

        appointment_id = str(ObjectId())  # Generate a unique appointment ID

        appointment_data = {
            'appointment_id': appointment_id,
            'doctor_name': doctor_name,
            'doctor_email': doctor_email,
            'appointment_date': appointment_date,
            'appointment_time': appointment_time,
            'patient_name': patient_name,
            'patient_email': patient_email
        }

        db = MongoDBHelper(collection="doctor-appointment")
        db.insert(appointment_data)
        print(request.form)
        return "Appointment booked successfully!"
    else:
        return "Invalid request method"


@web_app.route("/admin-patient-list")
def admin_patient_list():
    db = MongoDBHelper(collection="Hospital")
    patients = db.fetch_all()
    return render_template('admin-patient-list.html', patients=patients)


@web_app.route("/admin-doctor-list")
def admin_doctor_list():
    db = MongoDBHelper(collection="doctor-hospital")
    doctors = db.fetch_all()
    return render_template('admin-doctor-list.html', doctors=doctors)


@web_app.route("/admin-appointment-list")
def admin_appointment_list():
    db = MongoDBHelper(collection="doctor-appointment")
    appointments = db.fetch_all()
    print(appointments)
    return render_template('admin-appointment-list.html', appointments=appointments)


@web_app.route("/patient-appointment-list")
def patient_appointment_list():
    patient_email = session.get('email')
    db = MongoDBHelper(collection="doctor-appointment")
    appointments = db.fetch({'patient_email': patient_email})
    print(appointments)
    return render_template('patient-appointment-list.html', appointments=appointments)


@web_app.route("/cancel-appointment", methods=['POST'])
def cancel_appointment():
    if request.method == 'POST':
        appointment_id = request.form.get('appointment_id')

        db = MongoDBHelper(collection="doctor-appointment")
        db.update_appointment_cancel_by_patient(appointment_id)

        return redirect('/patient-appointment-list')
    else:
        return "Invalid request method"


@web_app.route("/doctor-appointment-list")
def doctor_appointment_list():
    doctor_email = session.get('doctor_email')  # Assuming doctor's email is stored in the session
    db = MongoDBHelper(collection="doctor-appointment")
    appointments = db.fetch({'doctor_email': doctor_email})  # Fetch appointments by doctor's email
    print(appointments)
    return render_template('doctor-appointment-list.html', appointments=appointments)


@web_app.route("/cancel-doctor-appointment", methods=['POST'])
def cancel_doctor_appointment():
    if request.method == 'POST':
        appointment_id = request.form.get('appointment_id')

        db = MongoDBHelper(collection="doctor-appointment")
        appointment = db.find_one({'appointment_id': appointment_id})
        if appointment:
            # Update the status to "cancel by doctor"
            db.update_one({'appointment_id': appointment_id}, {'$set': {'status': 'cancel by doctor'}})
            print("Appointment canceled by doctor.")
            return redirect('/doctor-appointment-list')  # Redirect to appointment list page
        else:
            return render_template('error.html', message="Appointment not found.")
    else:
        return "Invalid request method"



if __name__ == "__main__":
    web_app.run(port=1000)