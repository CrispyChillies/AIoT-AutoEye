from flask import Flask, request, jsonify
from flask_cors import CORS  # Add this import
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import DuplicateKeyError, ConnectionFailure
from bson import ObjectId
from werkzeug.utils import secure_filename
import base64
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
print(MONGO_URI)
try:
    client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
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


@app.route("/traffic", methods=["POST"])
def create_traffic_data():
    try:
        if not client:
            return jsonify({"error": "Database connection not available"}), 500

        _id = None
        traffic_doc = {}

        if request.is_json:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No JSON data provided"}), 400

            _id = data.get("_id")
            if not _id:
                # Auto-generate ID if not provided
                _id = f"traffic_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')[:-3]}"

            # Validate base64 image if provided
            image_data = data.get("image")
            if image_data:
                try:
                    base64.b64decode(image_data)
                    print(f"✅ Valid base64 image provided, length: {len(image_data)}")
                except Exception as e:
                    print(f"❌ Invalid base64 image: {str(e)}")
                    return jsonify({"error": "Invalid base64 image format"}), 400

            traffic_doc = {
                "_id": _id,
                "timestamp": data.get("timestamp", datetime.utcnow().isoformat() + "Z"),
                "location": data.get("location", "Unknown Location"),
                "vehicle_count": int(data.get("vehicle_count", 0)),
                "car_count": (
                    int(data.get("car_count"))
                    if data.get("car_count") is not None
                    else None
                ),
                "motorbike_count": (
                    int(data.get("motorbike_count"))
                    if data.get("motorbike_count") is not None
                    else None
                ),
                "lane1_in": (
                    int(data.get("lane1_in"))
                    if data.get("lane1_in") is not None
                    else None
                ),
                "lane1_out": (
                    int(data.get("lane1_out"))
                    if data.get("lane1_out") is not None
                    else None
                ),
                "lane2_in": (
                    int(data.get("lane2_in"))
                    if data.get("lane2_in") is not None
                    else None
                ),
                "lane2_out": (
                    int(data.get("lane2_out"))
                    if data.get("lane2_out") is not None
                    else None
                ),
                "status": data.get("status", "unknown"),
                "image": image_data,
            }

        else:
            # Handle multipart form data (file upload)
            _id = request.form.get("_id")
            if not _id:
                # Auto-generate ID if not provided
                _id = f"traffic_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')[:-3]}"

            # Handle image file upload and convert to base64
            image_file = request.files.get("image")
            image_data = None
            if image_file and image_file.filename:
                try:
                    # Validate file type
                    allowed_extensions = {"png", "jpg", "jpeg", "gif", "bmp", "webp"}
                    file_extension = (
                        image_file.filename.rsplit(".", 1)[1].lower()
                        if "." in image_file.filename
                        else ""
                    )

                    if file_extension not in allowed_extensions:
                        return (
                            jsonify(
                                {
                                    "error": f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
                                }
                            ),
                            400,
                        )

                    # Convert to base64
                    image_data = base64.b64encode(image_file.read()).decode("utf-8")
                    print(
                        f"📸 Image uploaded and converted: {image_file.filename}, size: {len(image_data)} chars"
                    )

                except Exception as e:
                    print(f"❌ Error processing image file: {str(e)}")
                    return jsonify({"error": f"Failed to process image: {str(e)}"}), 400

            # Helper function to safely convert to int
            def safe_int(value):
                if value is None or value == "":
                    return None
                try:
                    return int(value)
                except (ValueError, TypeError):
                    return None

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

        # Validate required fields
        if not traffic_doc["location"] or traffic_doc["location"] == "Unknown Location":
            if not request.form.get("location") and not (
                request.is_json and request.get_json().get("location")
            ):
                print("⚠️ Warning: No location provided, using 'Unknown Location'")

        if traffic_doc["vehicle_count"] < 0:
            return jsonify({"error": "vehicle_count must be >= 0"}), 400

        # Validate status
        valid_statuses = ["light", "moderate", "heavy", "unknown"]
        if traffic_doc["status"] not in valid_statuses:
            print(
                f"⚠️ Warning: Invalid status '{traffic_doc['status']}', using 'unknown'"
            )
            traffic_doc["status"] = "unknown"

        # Remove None values to keep the document clean
        traffic_doc = {k: v for k, v in traffic_doc.items() if v is not None}

        # Insert to database
        result = traffic_collection.insert_one(traffic_doc)
        print(f"✅ Traffic data inserted: {result.inserted_id}")

        # Return the created document with additional info
        created_doc = traffic_collection.find_one({"_id": result.inserted_id})

        return (
            jsonify(
                {
                    "message": "Traffic data created successfully",
                    "id": str(result.inserted_id),
                    "data": serialize_doc(created_doc),
                    "has_image": bool(traffic_doc.get("image")),
                    "auto_generated_id": _id
                    != (
                        request.form.get("_id")
                        if not request.is_json
                        else request.get_json().get("_id")
                    ),
                }
            ),
            201,
        )

    except DuplicateKeyError:
        return jsonify({"error": f"Traffic data with id '{_id}' already exists"}), 409
    except ValueError as e:
        return jsonify({"error": f"Invalid data format: {str(e)}"}), 400
    except Exception as e:
        print(f"❌ Error creating traffic data: {str(e)}")
        return jsonify({"error": str(e)}), 500


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
            "location",
            "vehicle_count",
            "status",
            "car_count",
            "motorbike_count",
            "lane1_in",
            "lane1_out",
            "lane2_in",
            "lane2_out",
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
