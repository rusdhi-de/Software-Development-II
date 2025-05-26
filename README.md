Here's a polished **README.md** file ready for your GitHub repository:

---

# Doctor Appointment Booking System

A web-based Doctor Appointment Booking System built with **Flask** and **SQLite**. This application allows patients to register, book appointments with doctors, and view prescriptions. Admins can manage appointments and add prescriptions securely.

## Demo

**Home Page:** `http://localhost:5000`
**Admin Login:**

* Email: `nub@gmail.com`
* Password: `nubcse`

(Admin is created automatically on first run.)

---

## Features

### Patients

* Register and log in
* View list of doctors and their specializations
* Book 30-minute appointments (max 2 per doctor/day)
* View your appointments
* View prescriptions and medicine reminders

### Admins

* Log in with secure credentials
* View and manage all appointments
* Cancel appointments
* Add/edit prescriptions for any patient

---

## Technologies Used

* **Python 3**
* **Flask**
* **Flask-Login**
* **SQLite**
* **SQLAlchemy**
* **HTML/CSS** with Bootstrap (for UI)

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/doctor-appointment-system.git
cd doctor-appointment-system
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the App

```bash
python app.py
```

Then go to: [http://localhost:5000](http://localhost:5000)

---

## Project Structure

```
doctor-appointment-system/
├── app.py
├── models.py
├── templates/
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   ├── doctor_list.html
│   ├── book_appointment.html
│   ├── patient_dashboard.html
│   ├── admin_dashboard.html
│   └── prescriptions.html
└── static/                # (Optional for custom CSS/JS)
```

---

## License

This project is licensed under the MIT License.
Feel free to use and modify it for educational or commercial purposes.
