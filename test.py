import json
import base64
import cv2
import numpy as np
from PIL import Image
import io


def load_json_data(json_file):
    """Load JSON data from file"""
    with open(json_file, "r") as file:
        data = json.load(file)
    return data


def decode_base64_image(base64_string):
    """Convert base64 string to OpenCV image"""
    try:
        # Decode base64 string
        image_data = base64.b64decode(base64_string)

        # Convert to PIL Image
        pil_image = Image.open(io.BytesIO(image_data))

        # Convert PIL to OpenCV format (BGR)
        opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

        return opencv_image
    except Exception as e:
        print(f"❌ Error decoding image: {str(e)}")
        return None


def draw_bboxes(image, bbox_data):
    """Draw bounding boxes on the image"""
    # Define colors for different classes
    colors = {
        0: (0, 255, 0),  # Green for cars (class 0)
        1: (0, 0, 255),  # Red for motorbikes (class 1)
    }

    # Define labels for classes
    labels = {0: "Car", 1: "Motorbike"}

    # Draw each bounding box
    for bbox in bbox_data:
        class_id = bbox["class"]
        lane = bbox["lane"]
        x = bbox["x"]
        y = bbox["y"]
        w = bbox["w"]
        h = bbox["h"]

        # Calculate rectangle coordinates
        x1, y1 = x, y
        x2, y2 = x + w, y + h

        # Get color for this class
        color = colors.get(class_id, (255, 255, 255))  # Default white if class unknown

        # Draw rectangle
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)

        # Create label text
        label_text = f"{labels.get(class_id, 'Unknown')} ({lane})"

        # Get text size for background rectangle
        (text_width, text_height), _ = cv2.getTextSize(
            label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
        )

        # Draw background rectangle for text
        cv2.rectangle(
            image, (x1, y1 - text_height - 10), (x1 + text_width, y1), color, -1
        )

        # Draw text
        cv2.putText(
            image,
            label_text,
            (x1, y1 - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )

    return image


def count_vehicles(bbox_data):
    """Count vehicles by class and lane"""
    counts = {
        "cars_in": 0,
        "cars_out": 0,
        "motorbikes_in": 0,
        "motorbikes_out": 0,
        "total": len(bbox_data),
    }

    for bbox in bbox_data:
        class_id = bbox["class"]
        lane = bbox["lane"]

        if class_id == 0:  # Car
            if lane == "in":
                counts["cars_in"] += 1
            elif lane == "out":
                counts["cars_out"] += 1
        elif class_id == 1:  # Motorbike
            if lane == "in":
                counts["motorbikes_in"] += 1
            elif lane == "out":
                counts["motorbikes_out"] += 1

    return counts


def main():
    json_file = "json_test.json"

    # Load JSON data
    print("📄 Loading JSON data...")
    data = load_json_data(json_file)

    # Extract image and bbox data
    base64_image = data.get("image")
    bbox_data = data.get("bbox", [])

    print(f"📊 Found {len(bbox_data)} bounding boxes")

    # Decode base64 image
    print("🖼️ Decoding base64 image...")
    image = decode_base64_image(base64_image)

    if image is None:
        print("❌ Failed to decode image")
        return

    print(f"✅ Image loaded: {image.shape}")

    # Count vehicles
    counts = count_vehicles(bbox_data)
    print(f"🚗 Vehicle counts: {counts}")

    # Draw bounding boxes
    print("🎨 Drawing bounding boxes...")
    image_with_boxes = draw_bboxes(image.copy(), bbox_data)

    # Add summary text to image
    summary_text = f"Cars: {counts['cars_in']+counts['cars_out']}, Motorbikes: {counts['motorbikes_in']+counts['motorbikes_out']}, Total: {counts['total']}"
    cv2.putText(
        image_with_boxes,
        summary_text,
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2,
    )
    cv2.putText(
        image_with_boxes,
        summary_text,
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 0, 0),
        1,
    )

    # Save the result
    output_filename = "output_with_bboxes.jpg"
    cv2.imwrite(output_filename, image_with_boxes)
    print(f"💾 Saved result to: {output_filename}")

    # Display the image (optional)
    cv2.imshow("Traffic Detection", image_with_boxes)
    print("👁️ Press any key to close the window...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
