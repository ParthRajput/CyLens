from flask import Flask, jsonify, render_template

from services.threat_services import get_all_threats


app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/threats")
def get_threats():
    threats = get_all_threats()

    return jsonify([dict(threat) for threat in threats])


if __name__ == "__main__":
    app.run(debug=True)