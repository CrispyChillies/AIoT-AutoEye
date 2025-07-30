from flask import Flask, jsonify
from flask_cors import CORS
from database import connect_db, client
from routes import users_bp, traffic_bp
from config import DEBUG

# Create Flask app
app = Flask(__name__)
CORS(app)

# Connect to database
connect_db()

# Register routes
app.register_blueprint(users_bp)
app.register_blueprint(traffic_bp)


# Health check
@app.route("/health", methods=["GET"])
def health_check():
    try:
        if client:
            client.admin.command("ping")
            return jsonify({"status": "healthy", "database": "connected"}), 200
        else:
            return jsonify({"status": "unhealthy", "database": "disconnected"}), 500
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=DEBUG, host="0.0.0.0", port=5000)
