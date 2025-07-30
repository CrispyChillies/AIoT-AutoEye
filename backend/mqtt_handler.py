import json
import paho.mqtt.client as mqtt
from datetime import datetime
from database import serialize_doc
import database
from config import (
    MQTT_BROKER,
    MQTT_PORT,
    MQTT_USERNAME,
    MQTT_PASSWORD,
    MQTT_TOPIC,
    MQTT_CLIENT_ID,
)
import threading


class MQTTHandler:
    def __init__(self):
        self.client = mqtt.Client(client_id=MQTT_CLIENT_ID)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.is_connected = False

        # Set credentials if provided
        if MQTT_USERNAME and MQTT_PASSWORD:
            self.client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    def on_connect(self, client, userdata, flags, rc):
        """Callback when MQTT client connects"""
        if rc == 0:
            print(f"✅ MQTT Connected to {MQTT_BROKER}:{MQTT_PORT}")
            self.is_connected = True
            # Subscribe to topic
            client.subscribe(MQTT_TOPIC)
            print(f"📡 Subscribed to topic: {MQTT_TOPIC}")
        else:
            print(f"❌ MQTT Connection failed with code {rc}")
            self.is_connected = False

    def on_disconnect(self, client, userdata, rc):
        """Callback when MQTT client disconnects"""
        print(f"🔌 MQTT Disconnected with code {rc}")
        self.is_connected = False

    def on_message(self, client, userdata, msg):
        """Callback when message is received"""
        try:
            print(f"📨 Received MQTT message on topic: {msg.topic}")

            # Parse JSON message
            message = json.loads(msg.payload.decode())
            print(
                f"🔍 Message from edge device - Frame ID: {message.get('frame_id', 'Unknown')}"
            )

            # Process the traffic data
            self.process_traffic_data(message)

        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in MQTT message: {e}")
        except Exception as e:
            print(f"❌ Error processing MQTT message: {e}")

    def process_traffic_data(self, mqtt_data):
        """Process traffic data from edge device and save to database"""
        try:
            if database.traffic_collection is None:
                print("❌ Traffic collection not available, skipping save")
                return False

            # Extract data from MQTT message
            frame_id = mqtt_data.get("frame_id", "unknown")
            timestamp = mqtt_data.get("timestamp", datetime.utcnow().isoformat() + "Z")
            location = mqtt_data.get("location", "Edge Device Camera")
            status = mqtt_data.get("status", "unknown")
            image_base64 = mqtt_data.get("image", "")
            bbox_data = mqtt_data.get("bbox", [])

            print(f"📋 Processing frame: {frame_id} from {location}")
            print(f"📦 Found {len(bbox_data)} detected objects")

            # Remove data URL prefix if present
            if image_base64 and image_base64.startswith("data:image"):
                image_base64 = image_base64.split(",")[1]

            # Count vehicles from bbox data
            cars_count = 0
            motorbikes_count = 0
            lane_in_count = 0
            lane_out_count = 0

            for bbox in bbox_data:
                vehicle_class = bbox.get("class")
                lane = bbox.get("lane", "unknown")

                # Count by vehicle type
                if vehicle_class == 0:  # Car
                    cars_count += 1
                elif vehicle_class == 1:  # Motorbike
                    motorbikes_count += 1

                # Count by lane direction
                if lane == "in":
                    lane_in_count += 1
                elif lane == "out":
                    lane_out_count += 1

            total_vehicles = cars_count + motorbikes_count

            # Override status if edge device didn't provide it or it's unknown
            if status == "unknown" or not status:
                if total_vehicles < 5:
                    status = "light"
                elif total_vehicles < 15:
                    status = "moderate"
                else:
                    status = "heavy"

            # Generate traffic document for database
            traffic_doc = {
                "_id": f"edge_{frame_id}_{datetime.now().strftime('%H%M%S')}",
                "timestamp": timestamp,
                "location": location,
                "vehicle_count": total_vehicles,
                "car_count": cars_count,
                "motorbike_count": motorbikes_count,
                "lane1_in": lane_in_count,
                "lane1_out": lane_out_count,
                "lane2_in": 0,  # Not specified in edge data
                "lane2_out": 0,  # Not specified in edge data
                "status": status,
                "image": image_base64 if image_base64 else None,
                # Additional metadata
                # "source": "edge_device",
                # "frame_id": frame_id,
                # "bbox_data": bbox_data,  # Store raw detection data
                # "detection_count": len(bbox_data),
            }

            # Remove None values to keep document clean
            traffic_doc = {
                k: v for k, v in traffic_doc.items() if v is not None and v != ""
            }

            # Save to database
            result = database.traffic_collection.insert_one(traffic_doc)

            print(f"✅ Traffic data saved - ID: {result.inserted_id}")
            print(
                f"📊 Summary: Cars={cars_count}, Motorbikes={motorbikes_count}, Total={total_vehicles}"
            )
            print(
                f"🚦 Status: {status}, Lane In={lane_in_count}, Lane Out={lane_out_count}"
            )
            print(f"📸 Image: {'Yes' if image_base64 else 'No'}")
            print("─" * 50)

            return True

        except Exception as e:
            print(f"❌ Error processing traffic data: {e}")
            print(f"📋 Failed frame data: {mqtt_data}")
            return False

    def start(self):
        """Start MQTT client in a separate thread"""

        def mqtt_loop():
            try:
                print(f"🔄 Connecting to MQTT broker: {MQTT_BROKER}:{MQTT_PORT}")
                self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
                self.client.loop_forever()
            except Exception as e:
                print(f"❌ MQTT connection error: {e}")

        mqtt_thread = threading.Thread(target=mqtt_loop, daemon=True)
        mqtt_thread.start()
        print(f"🚀 MQTT client started, connecting to {MQTT_BROKER}:{MQTT_PORT}")

    def stop(self):
        """Stop MQTT client"""
        if self.is_connected:
            self.client.disconnect()
        print("🛑 MQTT client stopped")

    def publish_test_message(self):
        """Publish a test message for debugging"""
        if self.is_connected:
            test_data = {
                "frame_id": "test_001",
                "timestamp": datetime.now().isoformat() + "Z",
                "location": "Test Location",
                "status": "moderate",
                "image": "",
                "bbox": [
                    {"class": 0, "lane": "in", "x": 100, "y": 150, "w": 80, "h": 120},
                    {"class": 1, "lane": "out", "x": 300, "y": 200, "w": 60, "h": 90},
                ],
            }
            self.client.publish(MQTT_TOPIC, json.dumps(test_data))
            print("📤 Test message published")
        else:
            print("❌ MQTT not connected, cannot publish test message")


# Global MQTT handler instance
mqtt_handler = MQTTHandler()
