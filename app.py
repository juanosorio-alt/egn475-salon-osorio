from decimal import Decimal, InvalidOperation
import os

import db
from flask import Flask, abort, redirect, render_template, request, url_for
# Import Flask so I can create a web application.
app = Flask(__name__)
app.config["DATABASE"] = os.path.join(app.instance_path, "salon.sqlite")
os.makedirs(app.instance_path, exist_ok=True)
db.init_app(app)
SAMPLE_SERVICES = [
    {"id": 1, "name": "Haircut", "description": "Haircut and basic styling", "price_cents": 3500, "duration_minutes": 30},
    {"id": 2, "name": "Hairstyling", "description": "Wash and blow-dry", "price_cents": 4500, "duration_minutes": 45},
    {"id": 3, "name": "Hair Coloring", "description": "Single-process hair color", "price_cents": 8500, "duration_minutes": 90},
    {"id": 4, "name": "Deep Conditioning", "description": "Moisturizing treatment for dry hair", "price_cents": 2500, "duration_minutes": 30},
    {"id": 5, "name": "Root Touch-Up", "description": "Color touch-up for new growth", "price_cents": 6000, "duration_minutes": 60},
    {"id": 6, "name": "Special Occasion Updo", "description": "Pinned hairstyle for special events", "price_cents": 7000, "duration_minutes": 60},
]
SAMPLE_CALENDAR = [
    {"time": "10:00 AM", "client": "Sofia Martinez", "service": "Haircut", "stylist": None, "status": "Pending"},
    {"time": "11:30 AM", "client": "Maya Rivera", "service": "Hairstyling", "stylist": "Ana", "status": "Confirmed"},
    {"time": "2:00 PM", "client": "Lena Diaz", "service": "Hair Coloring", "stylist": "Ana", "status": "Completed"},
]
SAMPLE_APPOINTMENTS = [
    {"service": "Haircut", "date": "Nov 14, 2026", "time": "10:00 AM", "status": "Pending"},
    {"service": "Hairstyling", "date": "Nov 21, 2026", "time": "11:30 AM", "status": "Confirmed"},
    {"service": "Hair Coloring", "date": "Nov 3, 2026", "time": "2:00 PM", "status": "Completed"},
    {"service": "Haircut", "date": "Nov 5, 2026", "time": "4:00 PM", "status": "Canceled"},
]
@app.route("/")
def home():
    return render_template("index.html")
    
# Define the function that handles requests to the home page.
# Connect the about page URL to the function below.
@app.route("/about")
def about():
    return "Bella Vista Salon is a salon in Coral Gables where clients can book services."
    # Return the salon description displayed on the about page.
@app.route("/services")
def services():
    services = db.get_db().execute(
        """
        SELECT id, name, description, duration_minutes, price_cents, active
        FROM services
        WHERE active = 1
        ORDER BY name
        """
    ).fetchall()
    return render_template("services.html", services=services)


@app.route("/services/<int:service_id>")
def service_detail(service_id):
    service = db.get_db().execute(
        "SELECT id, name, description, duration_minutes, price_cents, active "
        "FROM services WHERE id = ?",
        (service_id,),
    ).fetchone()
    if service is None:
        abort(404)
    return render_template("service_detail.html", service=service)


@app.route("/book")
def book():
    return render_template("book.html", services=SAMPLE_SERVICES)
@app.route("/calendar")
def calendar():
    return render_template("calendar.html", appointments=SAMPLE_CALENDAR)
@app.route("/appointments")
def appointments():
    return render_template("appointments.html", appointments=SAMPLE_APPOINTMENTS)
@app.route("/services/admin")
def services_admin():
    return render_template("services_admin.html", services=SAMPLE_SERVICES)


@app.route("/admin/services/new", methods=["GET", "POST"])
def service_new():
    form_values = {
        "name": "",
        "description": "",
        "price": "",
        "duration_minutes": "",
    }
    errors = []

    if request.method == "POST":
        form_values = {
            "name": request.form.get("name", ""),
            "description": request.form.get("description", ""),
            "price": request.form.get("price", ""),
            "duration_minutes": request.form.get("duration_minutes", ""),
        }

        name = form_values["name"].strip()
        if not name:
            errors.append("Service name is required.")

        price_cents = 0
        try:
            price = Decimal(form_values["price"])
            if not price.is_finite() or price < 0:
                errors.append("Price must be a valid non-negative amount.")
            else:
                cents = price * 100
                if cents != cents.to_integral_value():
                    errors.append("Price must have no more than two decimal places.")
                else:
                    price_cents = int(cents)
        except InvalidOperation:
            errors.append("Enter a valid price in dollars.")

        duration_minutes = 0
        try:
            duration_minutes = int(form_values["duration_minutes"])
            if duration_minutes <= 0:
                errors.append("Duration must be a positive whole number of minutes.")
        except ValueError:
            errors.append("Duration must be a positive whole number of minutes.")

        if not errors:
            db.get_db().execute(
                """
                INSERT INTO services
                    (name, description, price_cents, duration_minutes, active)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    name,
                    form_values["description"],
                    price_cents,
                    duration_minutes,
                    1,
                ),
            )
            db.get_db().commit()
            return redirect(url_for("services"))

    return render_template("service_new.html", form_values=form_values, errors=errors)
