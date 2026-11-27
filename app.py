from datetime import date, datetime, time as datetime_time
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

ALLOWED_STATUS_TRANSITIONS = {
    "requested": ("confirmed", "canceled"),
    "confirmed": ("completed", "canceled"),
    "completed": (),
    "canceled": (),
}


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


def validate_appointment(form):
    errors = []

    client_name = form.get("client_name", "")
    if not isinstance(client_name, str) or not client_name.strip():
        errors.append("Client name is required.")

    try:
        service_id = int(form.get("service_id", ""))
    except (TypeError, ValueError):
        errors.append("Choose an available service.")
    else:
        if not 1 <= service_id <= 9223372036854775807:
            errors.append("Choose an available service.")
        elif db.get_db().execute(
            "SELECT 1 FROM services WHERE id = ? AND active = 1",
            (service_id,),
        ).fetchone() is None:
            errors.append("Choose an available service.")

    date_value = form.get("date", "")
    try:
        appointment_date = date.fromisoformat(date_value)
        if appointment_date.isoformat() != date_value:
            raise ValueError
    except (TypeError, ValueError):
        errors.append("Enter a valid date in YYYY-MM-DD format.")
    else:
        if appointment_date < date.today():
            errors.append("Appointment date cannot be in the past.")

    time_value = form.get("time", "")
    try:
        appointment_time = datetime.strptime(time_value, "%H:%M").time()
        if appointment_time.strftime("%H:%M") != time_value:
            raise ValueError
    except (TypeError, ValueError):
        errors.append("Enter a valid time in HH:MM format.")
    else:
        if not datetime_time(9, 0) <= appointment_time <= datetime_time(17, 30):
            errors.append("Appointment time must be between 09:00 and 17:30.")

    return errors


def _get_appointments():
    return db.get_db().execute(
        """
        SELECT a.id, a.client_name, a.service_id, s.name AS service_name,
               a.date, a.time, a.notes, a.status
        FROM appointments AS a
        JOIN services AS s ON s.id = a.service_id
        ORDER BY a.date, a.time, a.id
        """
    ).fetchall()


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


@app.route("/book", methods=["GET", "POST"])
def book():
    connection = db.get_db()
    services = connection.execute(
        """
        SELECT id, name, price_cents
        FROM services
        WHERE active = 1
        ORDER BY name
        """
    ).fetchall()
    form_values = {
        "client_name": "",
        "service_id": "",
        "date": "",
        "time": "",
        "notes": "",
    }
    errors = []

    if request.method == "POST":
        form_values = {
            "client_name": request.form.get("client_name", ""),
            "service_id": request.form.get("service_id", ""),
            "date": request.form.get("date", ""),
            "time": request.form.get("time", ""),
            "notes": request.form.get("notes", ""),
        }
        errors = validate_appointment(request.form)

        if not errors:
            connection.execute(
                """
                INSERT INTO appointments
                    (client_name, service_id, date, time, notes, status, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    form_values["client_name"].strip(),
                    int(form_values["service_id"]),
                    form_values["date"],
                    form_values["time"],
                    form_values["notes"],
                    "requested",
                    None,
                ),
            )
            connection.commit()
            flash("Appointment request submitted successfully.", "success")
            return redirect(url_for("appointments"))

    available_service_ids = {str(service["id"]) for service in services}
    return render_template(
        "book.html",
        services=services,
        available_service_ids=available_service_ids,
        form_values=form_values,
        errors=errors,
    )


@app.route("/calendar")
def calendar():
    return render_template(
        "calendar.html",
        appointments=_get_appointments(),
        allowed_transitions=ALLOWED_STATUS_TRANSITIONS,
    )


@app.route("/appointments")
def appointments():
    return render_template("appointments.html", appointments=_get_appointments())


@app.route("/appointments/<int:appointment_id>/status", methods=["POST"])
def appointment_status(appointment_id):
    connection = db.get_db()
    appointment = connection.execute(
        "SELECT id, status FROM appointments WHERE id = ?",
        (appointment_id,),
    ).fetchone()
    if appointment is None:
        abort(404)

    current_status = appointment["status"]
    submitted_current_status = request.form.get("current_status")
    if (
        submitted_current_status is not None
        and submitted_current_status != current_status
    ):
        flash(
            "This appointment status has changed. Refresh the calendar before trying again.",
            "error",
        )
        return redirect(url_for("calendar"))

    requested_status = request.form.get("status", "")
    if requested_status not in ALLOWED_STATUS_TRANSITIONS.get(current_status, ()):
        flash("That appointment status change is not allowed.", "error")
        return redirect(url_for("calendar"))

    result = connection.execute(
        """
        UPDATE appointments
        SET status = ?
        WHERE id = ? AND status = ?
        """,
        (requested_status, appointment_id, current_status),
    )
    if result.rowcount != 1:
        flash(
            "This appointment status changed before your update. Refresh the calendar and try again.",
            "error",
        )
        return redirect(url_for("calendar"))

    connection.commit()
    flash(f"Appointment status updated to {requested_status}.", "success")
    return redirect(url_for("calendar"))


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
