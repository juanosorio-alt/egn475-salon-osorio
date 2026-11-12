from flask import Flask, abort, render_template
# Import Flask so I can create a web application.
app = Flask(__name__)
SAMPLE_SERVICES = [
    {"id": 1, "name": "Haircut", "description": "Haircut and basic styling", "price_cents": 3500, "duration_minutes": 30},
    {"id": 2, "name": "Hairstyling", "description": "Wash and blow-dry", "price_cents": 4500, "duration_minutes": 45},
    {"id": 3, "name": "Hair Coloring", "description": "Single-process hair color", "price_cents": 8500, "duration_minutes": 90},
    {"id": 4, "name": "Deep Conditioning", "description": "Moisturizing treatment for dry hair", "price_cents": 2500, "duration_minutes": 30},
    {"id": 5, "name": "Root Touch-Up", "description": "Color touch-up for new growth", "price_cents": 6000, "duration_minutes": 60},
    {"id": 6, "name": "Special Occasion Updo", "description": "Pinned hairstyle for special events", "price_cents": 7000, "duration_minutes": 60},
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
    return render_template("services.html", services=SAMPLE_SERVICES)
@app.route("/services/<int:service_id>")
def service_detail(service_id):
    service = next(
        (item for item in SAMPLE_SERVICES if item["id"] == service_id),
        None,
    )
    if service is None:
        abort(404)
    return render_template("service_detail.html", service=service)
@app.route("/book")
def book():
    return render_template("book.html", services=SAMPLE_SERVICES)