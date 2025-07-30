from flask import Flask, jsonify
from flask_cors import CORS
from database import connect_db, client
from routes import users_bp, traffic_bp
from config import DEBUG
from mqtt_handler import mqtt_handler

# Create Flask app
app = Flask(__name__)
CORS(app)

# Connect to database
connect_db()

# Start MQTT client
mqtt_handler.start()

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


@app.route("/mqtt/status", methods=["GET"])
def mqtt_status():
    return (
        jsonify(
            {
                "mqtt_connected": mqtt_handler.is_connected,
                "topic": "traffic/data",
                "broker": f"localhost:1883",
            }
        ),
        200,
    )


@app.route("/mqtt/test", methods=["POST"])
def mqtt_test():
    """Publish a test message to MQTT for debugging"""
    try:
        if mqtt_handler.is_connected:
            mqtt_handler.publish_test_message()
            return (
                jsonify(
                    {"message": "Test message sent successfully", "status": "success"}
                ),
                200,
            )
        else:
            return (
                jsonify({"error": "MQTT client not connected", "status": "failed"}),
                503,
            )
    except Exception as e:
        return (
            jsonify(
                {"error": f"Failed to send test message: {str(e)}", "status": "error"}
            ),
            500,
        )


if __name__ == "__main__":
    try:
        # Disable auto-reloader to prevent Flask restart
        app.run(debug=DEBUG, host="0.0.0.0", port=5000, use_reloader=False)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        mqtt_handler.stop()
