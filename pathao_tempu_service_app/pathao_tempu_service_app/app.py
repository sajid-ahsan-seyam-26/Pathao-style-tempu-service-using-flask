from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tempu_service.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# =========================
# DATABASE MODELS
# =========================
class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    nid = db.Column(db.String(30), nullable=True)
    license_no = db.Column(db.String(50), nullable=True)
    service_area = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default="Available")  # Available / Busy / Offline
    rating = db.Column(db.Float, default=5.0)
    total_rides = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    vehicles = db.relationship("Vehicle", backref="driver", lazy=True)
    rides = db.relationship("Ride", backref="driver", lazy=True)


class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plate_number = db.Column(db.String(50), nullable=False, unique=True)
    model = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, default=4)
    owner_name = db.Column(db.String(100), nullable=False)
    route_name = db.Column(db.String(100), nullable=False)
    fitness_expiry = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(20), default="Active")  # Active / Maintenance / Inactive
    driver_id = db.Column(db.Integer, db.ForeignKey("driver.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    rides = db.relationship("Ride", backref="vehicle", lazy=True)


class Ride(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    passenger_name = db.Column(db.String(100), nullable=False)
    passenger_phone = db.Column(db.String(20), nullable=False)
    pickup_location = db.Column(db.String(150), nullable=False)
    dropoff_location = db.Column(db.String(150), nullable=False)
    distance_km = db.Column(db.Float, nullable=False)
    passenger_count = db.Column(db.Integer, default=1)
    payment_method = db.Column(db.String(30), default="Cash")
    fare = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(30), default="Pending")  # Pending / Accepted / On Trip / Completed / Cancelled
    notes = db.Column(db.Text, nullable=True)
    rating = db.Column(db.Integer, nullable=True)
    driver_id = db.Column(db.Integer, db.ForeignKey("driver.id"), nullable=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicle.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SupportTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    issue_type = db.Column(db.String(80), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), default="Open")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# =========================
# HELPER FUNCTIONS
# =========================
def calculate_fare(distance_km, passenger_count):
    """Simple Bangladesh-friendly fare formula.
    Beginner-friendly calculation:
    - Base fare: 30 BDT
    - Per kilometer: 18 BDT
    - Extra passenger charge after 1 passenger: 10 BDT each
    """
    base_fare = 30
    per_km_rate = 18
    extra_passenger_charge = 0

    if passenger_count > 1:
        extra_passenger_charge = (passenger_count - 1) * 10

    total_fare = base_fare + (distance_km * per_km_rate) + extra_passenger_charge
    return int(round(total_fare))


def get_available_driver_and_vehicle():
    """Find one available driver with an active vehicle."""
    available_driver = Driver.query.filter_by(status="Available").first()

    if available_driver:
        active_vehicle = Vehicle.query.filter_by(driver_id=available_driver.id, status="Active").first()
        if active_vehicle:
            return available_driver, active_vehicle

    return None, None


def seed_data():
    """Add demo data only if the database is empty."""
    if Driver.query.count() == 0:
        drivers = [
            Driver(name="Md. Rahim Uddin", phone="01710000001", nid="1990XXXXXXXX", license_no="DL-DHK-1020", service_area="Mirpur", status="Available", rating=4.8, total_rides=126),
            Driver(name="Abdul Karim", phone="01820000002", nid="1988XXXXXXXX", license_no="DL-CTG-8801", service_area="Chattogram", status="Available", rating=4.7, total_rides=98),
            Driver(name="Jamal Hossain", phone="01930000003", nid="1995XXXXXXXX", license_no="DL-SYL-5502", service_area="Sylhet", status="Busy", rating=4.6, total_rides=77),
        ]
        db.session.add_all(drivers)
        db.session.commit()

    if Vehicle.query.count() == 0:
        vehicles = [
            Vehicle(plate_number="DHAKA-METRO-THA-11-2233", model="Bajaj RE CNG Tempu", capacity=4, owner_name="Md. Rahim Uddin", route_name="Mirpur 10 - Farmgate", fitness_expiry="2026-12-20", status="Active", driver_id=1),
            Vehicle(plate_number="CHATTA-METRO-THA-17-4433", model="TVS King Deluxe", capacity=4, owner_name="Abdul Karim", route_name="New Market - GEC", fitness_expiry="2026-10-15", status="Active", driver_id=2),
            Vehicle(plate_number="SYLHET-THA-14-9088", model="Mahindra Alfa", capacity=4, owner_name="Jamal Hossain", route_name="Zindabazar - Airport Road", fitness_expiry="2026-08-05", status="Maintenance", driver_id=3),
        ]
        db.session.add_all(vehicles)
        db.session.commit()


# =========================
# ROUTES
# =========================
@app.route("/")
def home():
    total_drivers = Driver.query.count()
    available_drivers = Driver.query.filter_by(status="Available").count()
    total_vehicles = Vehicle.query.count()
    active_vehicles = Vehicle.query.filter_by(status="Active").count()
    total_rides = Ride.query.count()
    completed_rides = Ride.query.filter_by(status="Completed").count()
    recent_rides = Ride.query.order_by(Ride.created_at.desc()).limit(5).all()

    total_earning = db.session.query(db.func.sum(Ride.fare)).filter_by(status="Completed").scalar()
    if total_earning is None:
        total_earning = 0

    return render_template(
        "home.html",
        total_drivers=total_drivers,
        available_drivers=available_drivers,
        total_vehicles=total_vehicles,
        active_vehicles=active_vehicles,
        total_rides=total_rides,
        completed_rides=completed_rides,
        total_earning=total_earning,
        recent_rides=recent_rides,
    )


@app.route("/book", methods=["GET", "POST"])
def book_ride():
    if request.method == "POST":
        passenger_name = request.form.get("passenger_name")
        passenger_phone = request.form.get("passenger_phone")
        pickup_location = request.form.get("pickup_location")
        dropoff_location = request.form.get("dropoff_location")
        distance_km = float(request.form.get("distance_km"))
        passenger_count = int(request.form.get("passenger_count"))
        payment_method = request.form.get("payment_method")
        notes = request.form.get("notes")

        fare = calculate_fare(distance_km, passenger_count)
        driver, vehicle = get_available_driver_and_vehicle()

        ride_status = "Pending"
        driver_id = None
        vehicle_id = None

        if driver and vehicle:
            ride_status = "Accepted"
            driver_id = driver.id
            vehicle_id = vehicle.id
            driver.status = "Busy"

        new_ride = Ride(
            passenger_name=passenger_name,
            passenger_phone=passenger_phone,
            pickup_location=pickup_location,
            dropoff_location=dropoff_location,
            distance_km=distance_km,
            passenger_count=passenger_count,
            payment_method=payment_method,
            fare=fare,
            status=ride_status,
            notes=notes,
            driver_id=driver_id,
            vehicle_id=vehicle_id,
        )

        db.session.add(new_ride)
        db.session.commit()

        flash("Ride request created successfully!", "success")
        return redirect(url_for("booking_success", ride_id=new_ride.id))

    return render_template("book.html")


@app.route("/booking-success/<int:ride_id>")
def booking_success(ride_id):
    ride = Ride.query.get_or_404(ride_id)
    return render_template("booking_success.html", ride=ride)


@app.route("/api/fare")
def api_fare():
    try:
        distance = float(request.args.get("distance", 0))
        passengers = int(request.args.get("passengers", 1))
        fare = calculate_fare(distance, passengers)
        return jsonify({"fare": fare, "distance": distance, "passengers": passengers})
    except ValueError:
        return jsonify({"error": "Invalid number"}), 400


@app.route("/admin")
def admin_dashboard():
    drivers = Driver.query.order_by(Driver.created_at.desc()).limit(5).all()
    vehicles = Vehicle.query.order_by(Vehicle.created_at.desc()).limit(5).all()
    rides = Ride.query.order_by(Ride.created_at.desc()).limit(8).all()
    tickets = SupportTicket.query.order_by(SupportTicket.created_at.desc()).limit(5).all()

    total_fare = db.session.query(db.func.sum(Ride.fare)).scalar()
    if total_fare is None:
        total_fare = 0

    completed_income = db.session.query(db.func.sum(Ride.fare)).filter_by(status="Completed").scalar()
    if completed_income is None:
        completed_income = 0

    pending_rides = Ride.query.filter_by(status="Pending").count()

    return render_template(
        "admin.html",
        drivers=drivers,
        vehicles=vehicles,
        rides=rides,
        tickets=tickets,
        total_fare=total_fare,
        completed_income=completed_income,
        pending_rides=pending_rides,
    )


@app.route("/drivers", methods=["GET", "POST"])
def drivers():
    if request.method == "POST":
        new_driver = Driver(
            name=request.form.get("name"),
            phone=request.form.get("phone"),
            nid=request.form.get("nid"),
            license_no=request.form.get("license_no"),
            service_area=request.form.get("service_area"),
            status=request.form.get("status"),
        )
        db.session.add(new_driver)
        db.session.commit()
        flash("Driver added successfully!", "success")
        return redirect(url_for("drivers"))

    all_drivers = Driver.query.order_by(Driver.created_at.desc()).all()
    return render_template("drivers.html", drivers=all_drivers)


@app.route("/vehicles", methods=["GET", "POST"])
def vehicles():
    if request.method == "POST":
        driver_id_value = request.form.get("driver_id")
        driver_id = None
        if driver_id_value:
            driver_id = int(driver_id_value)

        new_vehicle = Vehicle(
            plate_number=request.form.get("plate_number"),
            model=request.form.get("model"),
            capacity=int(request.form.get("capacity")),
            owner_name=request.form.get("owner_name"),
            route_name=request.form.get("route_name"),
            fitness_expiry=request.form.get("fitness_expiry"),
            status=request.form.get("status"),
            driver_id=driver_id,
        )
        db.session.add(new_vehicle)
        db.session.commit()
        flash("Vehicle added successfully!", "success")
        return redirect(url_for("vehicles"))

    all_vehicles = Vehicle.query.order_by(Vehicle.created_at.desc()).all()
    all_drivers = Driver.query.order_by(Driver.name).all()
    return render_template("vehicles.html", vehicles=all_vehicles, drivers=all_drivers)


@app.route("/rides")
def rides():
    keyword = request.args.get("keyword", "").strip()
    status = request.args.get("status", "").strip()

    query = Ride.query

    if keyword:
        query = query.filter(
            db.or_(
                Ride.passenger_name.contains(keyword),
                Ride.passenger_phone.contains(keyword),
                Ride.pickup_location.contains(keyword),
                Ride.dropoff_location.contains(keyword),
            )
        )

    if status:
        query = query.filter_by(status=status)

    all_rides = query.order_by(Ride.created_at.desc()).all()
    return render_template("rides.html", rides=all_rides, keyword=keyword, selected_status=status)


@app.route("/rides/<int:ride_id>/status", methods=["POST"])
def update_ride_status(ride_id):
    ride = Ride.query.get_or_404(ride_id)
    new_status = request.form.get("status")
    ride.status = new_status

    if new_status == "Completed":
        if ride.driver:
            ride.driver.status = "Available"
            ride.driver.total_rides += 1

    if new_status == "Cancelled":
        if ride.driver:
            ride.driver.status = "Available"

    db.session.commit()
    flash("Ride status updated successfully!", "success")
    return redirect(url_for("rides"))


@app.route("/rides/<int:ride_id>/rate", methods=["POST"])
def rate_ride(ride_id):
    ride = Ride.query.get_or_404(ride_id)
    ride.rating = int(request.form.get("rating"))

    if ride.driver:
        old_rating = ride.driver.rating
        ride.driver.rating = round((old_rating + ride.rating) / 2, 1)

    db.session.commit()
    flash("Thanks for your rating!", "success")
    return redirect(url_for("booking_success", ride_id=ride.id))


@app.route("/support", methods=["GET", "POST"])
def support():
    if request.method == "POST":
        ticket = SupportTicket(
            name=request.form.get("name"),
            phone=request.form.get("phone"),
            issue_type=request.form.get("issue_type"),
            message=request.form.get("message"),
        )
        db.session.add(ticket)
        db.session.commit()
        flash("Support ticket submitted. Our team will contact you soon.", "success")
        return redirect(url_for("support"))

    tickets = SupportTicket.query.order_by(SupportTicket.created_at.desc()).all()
    return render_template("support.html", tickets=tickets)


@app.route("/tickets/<int:ticket_id>/close", methods=["POST"])
def close_ticket(ticket_id):
    ticket = SupportTicket.query.get_or_404(ticket_id)
    ticket.status = "Closed"
    db.session.commit()
    flash("Support ticket closed.", "success")
    return redirect(url_for("support"))


# =========================
# APP STARTER
# =========================
with app.app_context():
    db.create_all()
    seed_data()


if __name__ == "__main__":
    app.run(debug=True)
