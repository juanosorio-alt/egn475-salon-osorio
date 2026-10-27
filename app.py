from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    return "Welcome to Bella Vista Salon"


@app.route("/about")
def about():
    return "Bella Vista Salon is a salon in Coral Gables where clients can book services."
