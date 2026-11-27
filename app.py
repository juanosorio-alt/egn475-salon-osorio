from decimal import Decimal, DecimalException
import os

import db
from flask import Flask, abort, flash, redirect, render_template, request, url_for
# Import Flask so I can create a web application.
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev")
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


def validate_service(form):
    errors = []
    name = form.get("name", "").strip()
    if not name:
        errors.append("Service name is required.")
    elif len(name) > 80:
        errors.append("Service name must be 80 characters or fewer.")

    try:
        duration_minutes = int(form.get("duration_minutes", ""))
        if not 15 <= duration_minutes <= 240:
            errors.append("Duration must be between 15 and 240 whole minutes.")
    except (TypeError, ValueError):
        errors.append("Duration must be between 15 and 240 whole minutes.")

    try:
        _price_to_cents(form.get("price", ""))
    except ValueError as error:
        errors.append(str(error))

    if "active" in form and form.get("active") not in {"0", "1"}:
        errors.append("Choose whether the service is active.")

    return errors


def _price_to_cents(value):
    try:
        price = Decimal(value)
    except (DecimalException, TypeError, ValueError) as error:
        raise ValueError("Enter a valid price in dollars.") from error

    if not price.is_finite():
        raise ValueError("Price must be a finite amount greater than zero.")
    if price <= 0:
        raise ValueError("Price must be greater than zero.")
    if price > Decimal("92233720368547758.07"):
        raise ValueError("Price is too large to store.")

    sign, digits, exponent = price.as_tuple()
    digit_string = "".join(str(digit) for digit in digits)
    stripped_digits = digit_string.rstrip("0")
    normalized_exponent = exponent + len(digit_string) - len(stripped_digits)
    if normalized_exponent < -2:
        raise ValueError("Price must have no more than two decimal places.")

    cents = int(stripped_digits.lstrip("0") or "0") * 10 ** (normalized_exponent + 2)
    return -cents if sign else cents


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
    services = db.get_db().execute(
        """
        SELECT id, name, description, duration_minutes, price_cents, active
        FROM services
        ORDER BY name
        """
    ).fetchall()
    return render_template("services_admin.html", services=services)


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
        errors = validate_service(request.form)

        if not errors:
            name = form_values["name"].strip()
            price_cents = _price_to_cents(form_values["price"])
            duration_minutes = int(form_values["duration_minutes"])
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
            flash("Service created successfully.", "success")
            return redirect(url_for("services_admin"))

    return render_template("service_new.html", form_values=form_values, errors=errors)


@app.route("/services/<int:service_id>/edit", methods=["GET", "POST"])
def service_edit(service_id):
    connection = db.get_db()
    service = connection.execute(
        """
        SELECT id, name, description, duration_minutes, price_cents, active
        FROM services
        WHERE id = ?
        """,
        (service_id,),
    ).fetchone()
    if service is None:
        abort(404)

    form_values = {
        "name": service["name"],
        "description": service["description"],
        "price": f'{Decimal(service["price_cents"]) / 100:.2f}',
        "duration_minutes": str(service["duration_minutes"]),
        "active": str(service["active"]),
    }
    errors = []

    if request.method == "POST":
        form_values = {
            "name": request.form.get("name", ""),
            "description": request.form.get("description", ""),
            "price": request.form.get("price", ""),
            "duration_minutes": request.form.get("duration_minutes", ""),
            "active": request.form.get("active", ""),
        }
        errors = validate_service(request.form)

        if not errors:
            connection.execute(
                """
                UPDATE services
                SET name = ?, description = ?, duration_minutes = ?,
                    price_cents = ?, active = ?
                WHERE id = ?
                """,
                (
                    form_values["name"].strip(),
                    form_values["description"],
                    int(form_values["duration_minutes"]),
                    _price_to_cents(form_values["price"]),
                    int(form_values["active"]),
                    service_id,
                ),
            )
            connection.commit()
            flash("Service updated successfully.", "success")
            return redirect(url_for("services_admin"))

    return render_template(
        "service_edit.html",
        form_values=form_values,
        errors=errors,
        service_id=service_id,
    )


@app.route("/services/<int:service_id>/delete", methods=["POST"])
def service_delete(service_id):
    connection = db.get_db()
    service = connection.execute(
        "SELECT id FROM services WHERE id = ?",
        (service_id,),
    ).fetchone()
    if service is None:
        abort(404)

    appointment = connection.execute(
        "SELECT 1 FROM appointments WHERE service_id = ? LIMIT 1",
        (service_id,),
    ).fetchone()
    if appointment is not None:
        connection.execute(
            "UPDATE services SET active = 0 WHERE id = ?",
            (service_id,),
        )
        flash("This service has appointments and was deactivated instead of deleted.", "success")
    else:
        connection.execute(
            "DELETE FROM services WHERE id = ?",
            (service_id,),
        )
        flash("Service deleted successfully.", "success")

    connection.commit()
    return redirect(url_for("services_admin"))
