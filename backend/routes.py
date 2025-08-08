from flask import Blueprint, request, jsonify
from datetime import datetime
import base64

import pymongo
import database  # import users_collection, traffic_collection, serialize_doc, client
from config import ALLOWED_EXTENSIONS, VALID_STATUSES
from pymongo.errors import DuplicateKeyError
import mqtt_handler

# Create blueprints
users_bp = Blueprint("users", __name__)
traffic_bp = Blueprint("traffic", __name__)


# Helper functions
def generate_traffic_id():
    return f"traffic_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]}"


def safe_int(value):
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


# USER ROUTES
@users_bp.route("/users", methods=["POST"])
def create_user():
    try:
        data = request.get_json()
        if not data or not data.get("_id"):
            return jsonify({"error": "Missing _id"}), 400

        personal = data.get("personal", {})
        if not personal.get("name") or not personal.get("email"):
            return jsonify({"error": "Missing name or email"}), 400

        user_doc = {
            "_id": data["_id"],
            "personal": {"name": personal["name"], "email": personal["email"]},
        }

        result = database.users_collection.insert_one(user_doc)
        return jsonify({"message": "User created", "id": str(result.inserted_id)}), 201

    except DuplicateKeyError:
        return jsonify({"error": "User already exists"}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@users_bp.route("/users", methods=["GET"])
def get_users():
    try:
        users = list(database.users_collection.find())
        return jsonify([database.serialize_doc(user) for user in users]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@users_bp.route("/users/<user_id>", methods=["GET"])
def get_user(user_id):
    try:
        user = database.users_collection.find_one({"_id": user_id})
        if user:
            return jsonify(database.serialize_doc(user)), 200
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@users_bp.route("/users/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        result = database.users_collection.delete_one({"_id": user_id})
        if result.deleted_count:
            return jsonify({"message": "User deleted"}), 200
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# TRAFFIC ROUTES
@traffic_bp.route("/traffic", methods=["POST"])
def create_traffic():
    try:
        if not database.client:
            return jsonify({"error": "Database not connected"}), 500

        # Handle JSON or form data
        if request.is_json:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400

            _id = data.get("_id") or generate_traffic_id()

            # Validate image if provided
            image_data = data.get("image")
            if image_data:
                try:
                    base64.b64decode(image_data)
                except:
                    return jsonify({"error": "Invalid image format"}), 400

            traffic_doc = {
                "_id": _id,
                "timestamp": data.get("timestamp", datetime.utcnow().isoformat() + "Z"),
                "location": data.get("location", "Unknown Location"),
                "vehicle_count": int(data.get("vehicle_count", 0)),
                "car_count": safe_int(data.get("car_count")),
                "motorbike_count": safe_int(data.get("motorbike_count")),
                "lane1_in": safe_int(data.get("lane1_in")),
                "lane1_out": safe_int(data.get("lane1_out")),
                "lane2_in": safe_int(data.get("lane2_in")),
                "lane2_out": safe_int(data.get("lane2_out")),
                "status": data.get("status", "unknown"),
                "image": image_data,
            }
        else:
            # Handle form data with file upload
            _id = request.form.get("_id") or generate_traffic_id()

            # Process image file
            image_data = None
            image_file = request.files.get("image")
            if image_file and image_file.filename:
                file_ext = (
                    image_file.filename.rsplit(".", 1)[1].lower()
                    if "." in image_file.filename
                    else ""
                )
                if file_ext not in ALLOWED_EXTENSIONS:
                    return jsonify({"error": "Invalid file type"}), 400

                try:
                    image_data = base64.b64encode(image_file.read()).decode("utf-8")
                except Exception as e:
                    return jsonify({"error": f"Image processing failed: {str(e)}"}), 400

            traffic_doc = {
                "_id": _id,
                "timestamp": request.form.get(
                    "timestamp", datetime.utcnow().isoformat() + "Z"
                ),
                "location": request.form.get("location", "Unknown Location"),
                "vehicle_count": safe_int(request.form.get("vehicle_count")) or 0,
                "car_count": safe_int(request.form.get("car_count")),
                "motorbike_count": safe_int(request.form.get("motorbike_count")),
                "lane1_in": safe_int(request.form.get("lane1_in")),
                "lane1_out": safe_int(request.form.get("lane1_out")),
                "lane2_in": safe_int(request.form.get("lane2_in")),
                "lane2_out": safe_int(request.form.get("lane2_out")),
                "status": request.form.get("status", "unknown"),
                "image": image_data,
            }

        # Validate and clean data
        if traffic_doc["status"] not in VALID_STATUSES:
            traffic_doc["status"] = "unknown"

        # Remove None values
        traffic_doc = {k: v for k, v in traffic_doc.items() if v is not None}

        # Save to database
        result = database.traffic_collection.insert_one(traffic_doc)
        created_doc = database.traffic_collection.find_one({"_id": result.inserted_id})

        return (
            jsonify(
                {
                    "message": "Traffic data created",
                    "data": database.serialize_doc(created_doc),
                    "has_image": bool(traffic_doc.get("image")),
                }
            ),
            201,
        )

    except DuplicateKeyError:
        return jsonify({"error": "Traffic ID already exists"}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@traffic_bp.route("/traffic", methods=["GET"])
def get_traffic():
    try:
        # Optional filters
        query = {}
        if request.args.get("location"):
            query["location"] = request.args.get("location")
        if request.args.get("status"):
            query["status"] = request.args.get("status")

        # Get data sorted by latest first
        if (
            mqtt_handler.mqtt_handler_inst is not None
            and mqtt_handler.mqtt_handler_inst.is_init()
            and mqtt_handler.mqtt_handler_inst.is_connected
            and mqtt_handler.mqtt_handler_inst.current_data_mqtt is not None
        ):
            traffic_data = [
                mqtt_handler.mqtt_handler_inst.current_data_mqtt.queue[i]
                for i in range(mqtt_handler.mqtt_handler_inst.current_data_mqtt.qsize())
            ]
            print(traffic_data)
            return jsonify(traffic_data), 200
        else:
            traffic_data = list(
                database.traffic_collection.find(query)
                .sort("timestamp", pymongo.DESCENDING)
                .limit(10)
            )
            return jsonify([database.serialize_doc(data) for data in traffic_data]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@traffic_bp.route("/traffic/<traffic_id>", methods=["GET"])
def get_traffic_by_id(traffic_id):
    try:
        traffic_data = database.traffic_collection.find_one({"_id": traffic_id})
        if traffic_data:
            return jsonify(database.serialize_doc(traffic_data)), 200
        return jsonify({"error": "Traffic data not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@traffic_bp.route("/traffic/<traffic_id>", methods=["DELETE"])
def delete_traffic(traffic_id):
    try:
        result = database.traffic_collection.delete_one({"_id": traffic_id})
        if result.deleted_count:
            return jsonify({"message": "Traffic data deleted"}), 200
        return jsonify({"error": "Traffic data not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400
