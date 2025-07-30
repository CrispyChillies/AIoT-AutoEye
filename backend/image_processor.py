import base64
import cv2
import numpy as np
from PIL import Image
import io
from datetime import datetime


class TrafficImageProcessor:
    """Handle image processing for traffic detection visualization"""

    def __init__(self):
        # Define colors for different vehicle classes
        self.colors = {
            0: (0, 255, 0),  # Green for cars (class 0)
            1: (0, 0, 255),  # Red for motorbikes (class 1)
        }

        # Define labels for classes
        self.labels = {0: "Car", 1: "Motorbike"}

        # Font settings
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 0.6
        self.font_thickness = 2
        self.box_thickness = 2

    def decode_base64_image(self, base64_string):
        """Convert base64 string to OpenCV image"""
        try:
            # Remove data URL prefix if present
            if base64_string.startswith("data:image"):
                base64_string = base64_string.split(",")[1]

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

    def encode_image_to_base64(self, image, format="jpg", quality=85):
        """Convert OpenCV image back to base64"""
        try:
            if format.lower() == "jpg" or format.lower() == "jpeg":
                encode_params = [cv2.IMWRITE_JPEG_QUALITY, quality]
                _, buffer = cv2.imencode(".jpg", image, encode_params)
            elif format.lower() == "png":
                _, buffer = cv2.imencode(".png", image)
            else:
                _, buffer = cv2.imencode(".jpg", image)

            image_base64 = base64.b64encode(buffer).decode("utf-8")
            return image_base64

        except Exception as e:
            print(f"❌ Error encoding image: {str(e)}")
            return None

    def draw_bboxes(self, image, bbox_data):
        """Draw bounding boxes on the image"""
        if not bbox_data:
            return image

        # Work on a copy to avoid modifying original
        result_image = image.copy()

        # Draw each bounding box
        for bbox in bbox_data:
            class_id = bbox.get("class", -1)
            lane = bbox.get("lane", "unknown")
            x = bbox.get("x", 0)
            y = bbox.get("y", 0)
            w = bbox.get("w", 0)
            h = bbox.get("h", 0)

            # Calculate rectangle coordinates
            x1, y1 = int(x), int(y)
            x2, y2 = int(x + w), int(y + h)

            # Get color for this class
            color = self.colors.get(class_id, (255, 255, 255))  # Default white

            # Draw rectangle
            cv2.rectangle(result_image, (x1, y1), (x2, y2), color, self.box_thickness)

            # Create label text
            label_text = f"{self.labels.get(class_id, 'Unknown')} ({lane})"

            # Get text size for background rectangle
            (text_width, text_height), baseline = cv2.getTextSize(
                label_text, self.font, self.font_scale, self.font_thickness
            )

            # Draw background rectangle for text
            cv2.rectangle(
                result_image,
                (x1, y1 - text_height - 10),
                (x1 + text_width + 5, y1),
                color,
                -1,
            )

            # Draw text
            cv2.putText(
                result_image,
                label_text,
                (x1 + 2, y1 - 5),
                self.font,
                self.font_scale,
                (255, 255, 255),  # White text
                self.font_thickness,
            )

        return result_image

    def count_vehicles(self, bbox_data):
        """Count vehicles by class and lane"""
        counts = {
            "cars_in": 0,
            "cars_out": 0,
            "motorbikes_in": 0,
            "motorbikes_out": 0,
            "total": len(bbox_data),
            "cars_total": 0,
            "motorbikes_total": 0,
        }

        for bbox in bbox_data:
            class_id = bbox.get("class", -1)
            lane = bbox.get("lane", "unknown")

            if class_id == 0:  # Car
                counts["cars_total"] += 1
                if lane == "in":
                    counts["cars_in"] += 1
                elif lane == "out":
                    counts["cars_out"] += 1
            elif class_id == 1:  # Motorbike
                counts["motorbikes_total"] += 1
                if lane == "in":
                    counts["motorbikes_in"] += 1
                elif lane == "out":
                    counts["motorbikes_out"] += 1

        return counts

    def add_summary_text(self, image, counts, location=None, timestamp=None):
        """Add summary information to the image"""
        result_image = image.copy()

        # Create summary text
        summary_lines = [
            f"Cars: {counts['cars_total']}, Motorbikes: {counts['motorbikes_total']}, Total: {counts['total']}",
            f"In: {counts['cars_in'] + counts['motorbikes_in']}, Out: {counts['cars_out'] + counts['motorbikes_out']}",
        ]

        # Add location if provided
        if location:
            summary_lines.insert(0, f"Location: {location}")

        # Add timestamp if provided
        if timestamp:
            try:
                # Format timestamp
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                summary_lines.append(f"Time: {time_str}")
            except:
                summary_lines.append(f"Time: {timestamp}")

        # Draw each line
        y_offset = 30
        for i, line in enumerate(summary_lines):
            y_pos = y_offset + (i * 25)

            # Draw background (black with transparency effect)
            (text_width, text_height), _ = cv2.getTextSize(line, self.font, 0.7, 2)

            # White text with black outline for better visibility
            cv2.putText(
                result_image,
                line,
                (10, y_pos),
                self.font,
                0.7,
                (0, 0, 0),  # Black outline
                3,
            )
            cv2.putText(
                result_image,
                line,
                (10, y_pos),
                self.font,
                0.7,
                (255, 255, 255),  # White text
                2,
            )

        return result_image

    def process_traffic_image(
        self, base64_image, bbox_data, location=None, timestamp=None, add_summary=True
    ):
        """Complete image processing pipeline"""
        try:
            # Decode base64 image
            image = self.decode_base64_image(base64_image)
            if image is None:
                print("❌ Failed to decode base64 image")
                return None, None

            print(f"✅ Image decoded: {image.shape}")

            # Count vehicles
            counts = self.count_vehicles(bbox_data)
            print(f"📊 Vehicle counts: {counts}")

            # Draw bounding boxes
            image_with_boxes = self.draw_bboxes(image, bbox_data)
            print(f"🎨 Drew {len(bbox_data)} bounding boxes")

            # Add summary text if requested
            # if add_summary:
            #     image_with_boxes = self.add_summary_text(
            #         image_with_boxes, counts, location, timestamp
            #     )
            #     print("📝 Added summary text")

            # Encode back to base64
            processed_base64 = self.encode_image_to_base64(image_with_boxes)
            if processed_base64 is None:
                print("❌ Failed to encode processed image")
                return None, counts

            print("✅ Image processing complete")
            return processed_base64, counts

        except Exception as e:
            print(f"❌ Error in image processing pipeline: {str(e)}")
            return None, None

    def save_processed_image(self, image, filename):
        """Save processed image to file"""
        try:
            cv2.imwrite(filename, image)
            print(f"💾 Saved processed image to: {filename}")
            return True
        except Exception as e:
            print(f"❌ Error saving image: {str(e)}")
            return False


# # Example usage and testing
# if __name__ == "__main__":
#     # Test the image processor
#     processor = TrafficImageProcessor()

#     # Test data
#     sample_bbox = [
#         {"class": 0, "lane": "in", "x": 100, "y": 150, "w": 80, "h": 120},
#         {"class": 1, "lane": "out", "x": 300, "y": 200, "w": 60, "h": 90},
#     ]

#     print("🧪 TrafficImageProcessor initialized and ready for testing")
#     print(f"📊 Sample bbox data: {sample_bbox}")
#     print(f"🎨 Colors: {processor.colors}")
#     print(f"🏷️ Labels: {processor.labels}")
