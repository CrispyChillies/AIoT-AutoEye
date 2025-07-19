from flask import Flask, request, jsonify
from flask_cors import CORS  # Add this import
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, ConnectionFailure
from bson import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
print(MONGO_URI)
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    # Test the connection
    client.admin.command("ping")
    db = client["autoeye_db"]
    users_collection = db["users"]
    traffic_collection = db["traffic_data"]
    print("✅ MongoDB connected successfully")
except ConnectionFailure:
    print("❌ MongoDB connection failed")
    client = None


# Helper function to convert ObjectId to string
def serialize_doc(doc):
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


# User endpoints
@app.route("/users", methods=["POST"])
def create_user():
    try:
        if not client:
            return jsonify({"error": "Database connection not available"}), 500

        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Validate required fields
        if not data.get("_id"):
            return jsonify({"error": "_id is required"}), 400

        personal = data.get("personal", {})
        if not personal.get("name") or not personal.get("email"):
            return (
                jsonify({"error": "name and email are required in personal object"}),
                400,
            )

        user_doc = {
            "_id": data.get("_id"),
            "personal": {"name": personal.get("name"), "email": personal.get("email")},
        }

        result = users_collection.insert_one(user_doc)
        return jsonify({"message": "User created", "id": str(result.inserted_id)}), 201

    except DuplicateKeyError:
        return jsonify({"error": f"User with id '{data.get('_id')}' already exists"}), 409  # type: ignore
    except Exception as e:
        print(f"Error creating user: {str(e)}")
        return jsonify({"error": str(e)}), 400


@app.route("/users", methods=["GET"])
def get_users():
    try:
        users = list(users_collection.find())
        return jsonify([serialize_doc(user) for user in users]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/users/<user_id>", methods=["GET"])
def get_user(user_id):
    try:
        user = users_collection.find_one({"_id": user_id})
        if user:
            return jsonify(serialize_doc(user)), 200
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/users/<user_id>", methods=["PUT"])
def update_user(user_id):
    try:
        data = request.get_json()
        update_doc = {}
        if "personal" in data:
            update_doc["personal"] = data["personal"]

        result = users_collection.update_one({"_id": user_id}, {"$set": update_doc})
        if result.matched_count:
            return jsonify({"message": "User updated"}), 200
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/users/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        result = users_collection.delete_one({"_id": user_id})
        if result.deleted_count:
            return jsonify({"message": "User deleted"}), 200
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# Traffic data endpoints
@app.route("/traffic", methods=["POST"])
def create_traffic_data():
    try:
        if not client:
            return jsonify({"error": "Database connection not available"}), 500

        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Validate required field _id
        if not data.get("_id"):
            return jsonify({"error": "_id is required"}), 400

        # Optional: validate numeric fields
        numeric_fields = ["vehicle_count", "car_count", "motorbike_count", 
                          "lane1_in", "lane1_out", "lane2_in", "lane2_out"]
        for field in numeric_fields:
            if field in data and not isinstance(data[field], int):
                return jsonify({"error": f"{field} must be an integer"}), 400

        traffic_doc = {
            "_id": data["_id"],
            "timestamp": data.get("timestamp", datetime.utcnow().isoformat() + "Z"),
            "location": data.get("location"),
            "vehicle_count": data.get("vehicle_count", 0),
            "car_count": data.get("car_count", 0),
            "motorbike_count": data.get("motorbike_count", 0),
            "lane1_in": data.get("lane1_in", 0),
            "lane1_out": data.get("lane1_out", 0),
            "lane2_in": data.get("lane2_in", 0),
            "lane2_out": data.get("lane2_out", 0),
            "status": data.get("status"),
        }

        result = traffic_collection.insert_one(traffic_doc)
        return (
            jsonify({"message": "Traffic data created", "id": str(result.inserted_id)}),
            201,
        )

    except DuplicateKeyError:
        return jsonify({"error": f"Traffic data with id '{data.get('_id')}' already exists"}), 409
    except Exception as e:
        print(f"Error creating traffic data: {str(e)}")
        return jsonify({"error": str(e)}), 400


@app.route("/traffic", methods=["GET"])
def get_traffic_data():
    try:
        location = request.args.get("location")
        status = request.args.get("status")

        query = {}
        if location:
            query["location"] = location
        if status:
            query["status"] = status

        traffic_data = list(traffic_collection.find(query).sort("timestamp", -1))
        return jsonify([serialize_doc(data) for data in traffic_data]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/traffic/<traffic_id>", methods=["GET"])
def get_traffic_by_id(traffic_id):
    try:
        traffic_data = traffic_collection.find_one({"_id": traffic_id})
        if traffic_data:
            return jsonify(serialize_doc(traffic_data)), 200
        return jsonify({"error": "Traffic data not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/traffic/<traffic_id>", methods=["PUT"])
def update_traffic_data(traffic_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        update_doc = {}
        updatable_fields = [
            "location", "vehicle_count", "status",
            "car_count", "motorbike_count",
            "lane1_in", "lane1_out",
            "lane2_in", "lane2_out"
        ]

        for field in updatable_fields:
            if field in data:
                update_doc[field] = data[field]

        if not update_doc:
            return jsonify({"error": "No valid fields to update"}), 400

        result = traffic_collection.update_one(
            {"_id": traffic_id}, {"$set": update_doc}
        )

        if result.matched_count:
            return jsonify({"message": "Traffic data updated"}), 200
        return jsonify({"error": "Traffic data not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/traffic/<traffic_id>", methods=["DELETE"])
def delete_traffic_data(traffic_id):
    try:
        result = traffic_collection.delete_one({"_id": traffic_id})
        if result.deleted_count:
            return jsonify({"message": "Traffic data deleted"}), 200
        return jsonify({"error": "Traffic data not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# Add a health check endpoint
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
    app.run(debug=True, host="0.0.0.0", port=5000)
