from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# In-memory storage for testing
users_data = {}
traffic_data = {}


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "database": "in-memory"}), 200


@app.route("/users", methods=["POST"])
def create_user():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        user_id = data.get("_id")
        if not user_id:
            return jsonify({"error": "_id is required"}), 400

        if user_id in users_data:
            return jsonify({"error": f"User with id '{user_id}' already exists"}), 409

        personal = data.get("personal", {})
        if not personal.get("name") or not personal.get("email"):
            return (
                jsonify({"error": "name and email are required in personal object"}),
                400,
            )

        users_data[user_id] = data
        return jsonify({"message": "User created", "id": user_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/users", methods=["GET"])
def get_users():
    return jsonify(list(users_data.values())), 200


@app.route("/users/<user_id>", methods=["GET"])
def get_user(user_id):
    if user_id in users_data:
        return jsonify(users_data[user_id]), 200
    return jsonify({"error": "User not found"}), 404


@app.route("/users/<user_id>", methods=["PUT"])
def update_user(user_id):
    try:
        if user_id not in users_data:
            return jsonify({"error": "User not found"}), 404

        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Update the user data
        if "personal" in data:
            users_data[user_id]["personal"] = data["personal"]

        return jsonify({"message": "User updated"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/users/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    if user_id in users_data:
        del users_data[user_id]
        return jsonify({"message": "User deleted"}), 200
    return jsonify({"error": "User not found"}), 404


@app.route("/traffic", methods=["POST"])
def create_traffic_data():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        traffic_id = data.get("_id")
        if not traffic_id:
            return jsonify({"error": "_id is required"}), 400

        if traffic_id in traffic_data:
            return (
                jsonify(
                    {"error": f"Traffic data with id '{traffic_id}' already exists"}
                ),
                409,
            )

        if "timestamp" not in data:
            data["timestamp"] = datetime.utcnow().isoformat() + "Z"

        traffic_data[traffic_id] = data
        return jsonify({"message": "Traffic data created", "id": traffic_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/traffic", methods=["GET"])
def get_traffic_data():
    location = request.args.get("location")
    status = request.args.get("status")

    result = list(traffic_data.values())

    if location:
        result = [t for t in result if t.get("location") == location]
    if status:
        result = [t for t in result if t.get("status") == status]

    return jsonify(result), 200


@app.route("/traffic/<traffic_id>", methods=["GET"])
def get_traffic_by_id(traffic_id):
    if traffic_id in traffic_data:
        return jsonify(traffic_data[traffic_id]), 200
    return jsonify({"error": "Traffic data not found"}), 404


@app.route("/traffic/<traffic_id>", methods=["PUT"])
def update_traffic_data(traffic_id):
    try:
        if traffic_id not in traffic_data:
            return jsonify({"error": "Traffic data not found"}), 404

        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Update the traffic data
        for field in ["location", "vehicle_count", "status"]:
            if field in data:
                traffic_data[traffic_id][field] = data[field]

        return jsonify({"message": "Traffic data updated"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/traffic/<traffic_id>", methods=["DELETE"])
def delete_traffic_data(traffic_id):
    if traffic_id in traffic_data:
        del traffic_data[traffic_id]
        return jsonify({"message": "Traffic data deleted"}), 200
    return jsonify({"error": "Traffic data not found"}), 404


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
