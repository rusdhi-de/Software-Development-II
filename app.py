from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, Patient, Admin, Doctor, Appointment, Prescription
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///doctor_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    # Try to find Patient first
    user = Patient.query.get(int(user_id))
    if user:
        return user
    # Or Admin
    user = Admin.query.get(int(user_id))
    return user

@app.before_request
def create_tables():
    db.create_all()
    # Add dummy doctor if not exist
    if Doctor.query.count() == 0:
        d1 = Doctor(name="Dr. Kefayet", specialization="Cardiologist")
        d2 = Doctor(name="Dr. Rifat", specialization="Dermatologist")
        db.session.add_all([d1, d2])
        db.session.commit()
    # Add admin if not exist
    if Admin.query.filter_by(email="nub@gmail.com").first() is None:
        admin = Admin(email="nub@gmail.com", password=generate_password_hash("nubcse"))
        db.session.add(admin)
        db.session.commit()

# --- Routes ---

@app.route('/')
def home():
    return render_template('home.html')

# Patient Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        phone = request.form['phone']
        email = request.form['email']
        password = request.form['password']
        if Patient.query.filter((Patient.email == email) | (Patient.phone == phone)).first():
            flash("User with this phone/email already exists.")
            return redirect(url_for('register'))
        hashed_pw = generate_password_hash(password)
        new_patient = Patient(phone=phone, email=email, password=hashed_pw)
        db.session.add(new_patient)
        db.session.commit()
        flash("Registration successful. Please login.")
        return redirect(url_for('login'))
    return render_template('register.html')

# Patient Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = Patient.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Logged in successfully.")
            return redirect(url_for('patient_dashboard'))
        else:
            flash("Invalid credentials.")
            return redirect(url_for('login'))
    return render_template('login.html')

# Admin Login
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        admin = Admin.query.filter_by(email=email).first()
        if admin and check_password_hash(admin.password, password):
            login_user(admin)
            flash("Admin logged in.")
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid admin credentials.")
            return redirect(url_for('admin_login'))
    return render_template('admin_login.html')

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.")
    return redirect(url_for('home'))

# Doctor List
@app.route('/doctors')
@login_required
def doctor_list():
    doctors = Doctor.query.all()
    return render_template('doctor_list.html', doctors=doctors)

# Book Appointment
@app.route('/book/<int:doctor_id>', methods=['GET', 'POST'])
@login_required
def book_appointment(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    if request.method == 'POST':
        start_time_str = request.form['start_time']
        try:
            start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M")
        except ValueError:
            flash("Invalid datetime format.")
            return redirect(url_for('book_appointment', doctor_id=doctor_id))

        end_time = start_time + timedelta(minutes=30)

        # Check max 2 patients per doctor on that day
        day_start = datetime(start_time.year, start_time.month, start_time.day)
        day_end = day_start + timedelta(days=1)

        daily_appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            Appointment.start_time >= day_start,
            Appointment.start_time < day_end
        ).count()

        if daily_appointments >= 2:
            flash("Doctor already has 2 appointments on this day.")
            return redirect(url_for('doctor_list'))

        # Check time overlap
        overlapping = Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            Appointment.start_time < end_time,
            Appointment.end_time > start_time
        ).first()

        if overlapping:
            flash("This time slot is already booked.")
            return redirect(url_for('doctor_list'))

        # Book appointment
        new_appointment = Appointment(
            patient_id=current_user.id,
            doctor_id=doctor.id,
            start_time=start_time,
            end_time=end_time
        )
        db.session.add(new_appointment)
        db.session.commit()
        flash("Appointment booked successfully.")
        return redirect(url_for('patient_dashboard'))

    return render_template('book_appointment.html', doctor=doctor)

# Patient Dashboard
@app.route('/dashboard')
@login_required
def patient_dashboard():
    if isinstance(current_user._get_current_object(), Admin):
        return redirect(url_for('admin_dashboard'))

    appointments = Appointment.query.filter_by(patient_id=current_user.id).order_by(Appointment.start_time).all()
    prescriptions = Prescription.query.filter_by(patient_id=current_user.id).all()

    # Medicine reminders: Let's assume prescriptions with "take medicine" show here
    medicine_reminders = []
    for pres in prescriptions:
        if 'medicine' in pres.details.lower():
            medicine_reminders.append(pres)

    return render_template('patient_dashboard.html', appointments=appointments, prescriptions=prescriptions, medicine_reminders=medicine_reminders)

# Admin Dashboard
@app.route('/admin')
@login_required
def admin_dashboard():
    if not isinstance(current_user._get_current_object(), Admin):
        flash("Access denied.")
        return redirect(url_for('home'))

    appointments = Appointment.query.order_by(Appointment.start_time).all()
    return render_template('admin_dashboard.html', appointments=appointments)

# Cancel appointment (Admin)
@app.route('/cancel_appointment/<int:appointment_id>')
@login_required
def cancel_appointment(appointment_id):
    if not isinstance(current_user._get_current_object(), Admin):
        flash("Access denied.")
        return redirect(url_for('home'))
    appointment = Appointment.query.get_or_404(appointment_id)
    db.session.delete(appointment)
    db.session.commit()
    flash("Appointment canceled.")
    return redirect(url_for('admin_dashboard'))

# Add Prescription (Admin)
@app.route('/add_prescription/<int:appointment_id>', methods=['GET', 'POST'])
@login_required
def add_prescription(appointment_id):
    if not isinstance(current_user._get_current_object(), Admin):
        flash("Access denied.")
        return redirect(url_for('home'))

    appointment = Appointment.query.get_or_404(appointment_id)
    if request.method == 'POST':
        details = request.form['details']
        pres = Prescription.query.filter_by(appointment_id=appointment.id).first()
        if pres:
            pres.details = details
        else:
            pres = Prescription(appointment_id=appointment.id, patient_id=appointment.patient_id, details=details)
            db.session.add(pres)
        db.session.commit()
        flash("Prescription saved.")
        return redirect(url_for('admin_dashboard'))

    return render_template('prescriptions.html', appointment=appointment)

if __name__ == '__main__':
    app.run(debug=True)
