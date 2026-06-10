# TempuGo Bangladesh - Pathao-style Tempu Service App

A beginner-friendly Flask project for a Bangladesh local tempu/CNG ride service platform.

## Main Features

- Passenger ride booking
- Live fare calculation
- Driver management
- Vehicle/fleet management
- Automatic driver and vehicle assignment
- Ride status tracking
- Cash, bKash, Nagad, Rocket payment options
- Admin dashboard
- Support ticket system
- Ride rating system
- SQLite database using SQLAlchemy
- Professional responsive HTML/CSS/JS interface
- Uses the provided Bangladeshi tempu photo as background image

## Project Structure

```text
pathao_tempu_service_app/
│── app.py
│── requirements.txt
│── README.md
│── templates/
│   ├── base.html
│   ├── home.html
│   ├── book.html
│   ├── booking_success.html
│   ├── admin.html
│   ├── drivers.html
│   ├── vehicles.html
│   ├── rides.html
│   └── support.html
│── static/
│   ├── css/style.css
│   ├── js/main.js
│   └── images/tempu_background.jpg
```

## How to Run

1. Open terminal inside the project folder.
2. Install requirements:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python app.py
```

4. Open your browser:

```text
http://127.0.0.1:5000
```

## Notes for Beginners

- The database file will be created automatically inside the `instance` folder.
- Demo drivers and vehicles are inserted automatically when the database is empty.
- You can edit fare calculation inside `calculate_fare()` in `app.py`.
- You can edit design from `static/css/style.css`.
- You can edit frontend JavaScript from `static/js/main.js`.
