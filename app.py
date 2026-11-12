from flask import Flask, render_template
# Import Flask so I can create a web application.
app = Flask(__name__)
# Create the Flask application and store it in app.
# Connect the home page URL to the function below.
@app.route("/")
def home():
    return render_template("index.html")
    
# Define the function that handles requests to the home page.
# Connect the about page URL to the function below.
@app.route("/about")
def about():
    return "Bella Vista Salon is a salon in Coral Gables where clients can book services."
    # Return the salon description displayed on the about page.