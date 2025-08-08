import base64
import json
from datetime import datetime
from PIL import Image
import io
import random


# Create a black image (640x480) and convert to base64
def create_black_image_base64():
    img = Image.new("RGB", (640, 480), color="black")
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    img_bytes = buffer.getvalue()
    return base64.b64encode(img_bytes).decode("utf-8")


# Generate random bbox data
def generate_random_bbox():
    vehicles = []
    num_vehicles = random.randint(3, 12)

    for i in range(num_vehicles):
        vehicle_class = random.choice(["car", "motorbike"])
        lane = random.choice(["in", "out"])

        # Random coordinates within image bounds
        x = random.randint(50, 500)
        y = random.randint(50, 350)
        w = random.randint(60, 150)
        h = random.randint(80, 200)

        vehicles.append(
            {
                "class": vehicle_class,
                "lane": lane,
                "x": x,
                "y": y,
                "w": w,
                "h": h,
                "confidence": round(random.uniform(0.7, 0.95), 2),
            }
        )

    return vehicles


# Generate sample data
black_image_base64 = create_black_image_base64()
bbox_data = generate_random_bbox()

# Count vehicles
cars_count = len([b for b in bbox_data if b.get("class") == "car"])
motorbikes_count = len([b for b in bbox_data if b.get("class") == "motorbike"])
lane_in_count = len([b for b in bbox_data if b.get("lane") == "in"])
lane_out_count = len([b for b in bbox_data if b.get("lane") == "out"])
total_vehicles = len(bbox_data)

# Determine status
if total_vehicles < 5:
    status = "light"
elif total_vehicles < 15:
    status = "moderate"
else:
    status = "heavy"

# Create the fake traffic document
fake_traffic_doc = {
    "_id": f"edge_test_001_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
    "timestamp": datetime.now().isoformat() + "Z",
    "location": "Test Intersection - Main Street & Oak Ave",
    "vehicle_count": total_vehicles,
    "car_count": cars_count,
    "motorbike_count": motorbikes_count,
    "lane1_in": lane_in_count,
    "lane1_out": lane_out_count,
    "lane2_in": 0,
    "lane2_out": 0,
    "status": status,
    "image": black_image_base64,
    "bbox_data": bbox_data,
    "edge_id": "test_001",
    "source": "mqtt_edge_device",
}

with open("fake.json", "w") as file:
    json.dump(fake_traffic_doc, file, indent=2)

print(json.dumps(fake_traffic_doc, indent=2))
