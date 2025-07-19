import requests
import json
import base64
BASE_URL = "http://localhost:5000"

def test_health():
    """Test if the server and database are healthy"""
    print("=== Health Check ===")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health Check: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health Check Failed: {e}")
        return False

def cleanup_test_data():
    """Clean up test data before running tests"""
    try:
        requests.delete(f"{BASE_URL}/users/user123")
        requests.delete(f"{BASE_URL}/traffic/traffic123")
    except:
        pass  # Ignore errors if data doesn't exist

def test_users():
    print("=== Testing Users API ===")
    
    # Test creating a user
    user_data = {
        "_id": "user123",
        "personal": {
            "name": "John Doe",
            "email": "john@example.com"
        }
    }
    
    response = requests.post(f"{BASE_URL}/users", json=user_data)
    print(f"Create User: {response.status_code} - {response.json()}")
    
    # If creation failed, show the error details
    if response.status_code != 201:
        print(f"❌ User creation failed. Response: {response.text}")
        return False
    
    # Test getting all users
    response = requests.get(f"{BASE_URL}/users")
    print(f"Get All Users: {response.status_code} - Found {len(response.json())} users")
    
    # Test getting specific user
    response = requests.get(f"{BASE_URL}/users/user123")
    print(f"Get User by ID: {response.status_code} - {response.json()}")
    
    # Test updating user
    update_data = {
        "personal": {
            "name": "John Smith",
            "email": "johnsmith@example.com"
        }
    }
    response = requests.put(f"{BASE_URL}/users/user123", json=update_data)
    print(f"Update User: {response.status_code} - {response.json()}")
    
    # Verify update
    response = requests.get(f"{BASE_URL}/users/user123")
    if response.status_code == 200:
        user = response.json()
        print(f"Verified Update - Name: {user['personal']['name']}")
    
    return True

import matplotlib.pyplot as plt
from PIL import Image
import io

def test_traffic():
    print("\n=== Testing Traffic API ===")

    # Load image to be sent
    image_path = "5x5.jpg"
    with open(image_path, "rb") as img_file:
        files = {"image": ("5x5.jpg", img_file, "image/jpeg")}
        data = {
            "_id": "traffic123",
            "location": "Location A",
            "vehicle_count": "120",
            "car_count": "80",
            "motorbike_count": "40",
            "lane1_in": "30",
            "lane1_out": "25",
            "lane2_in": "20",
            "lane2_out": "15",
            "status": "HEAVY"
        }

        response = requests.post(f"{BASE_URL}/traffic", files=files, data=data)

    print(f"Create Traffic Data: {response.status_code} - {response.json()}")

    if response.status_code != 201:
        print(f"❌ Traffic data creation failed. Response: {response.text}")
        return False

    # Get the created traffic record
    response = requests.get(f"{BASE_URL}/traffic/traffic123")
    if response.status_code == 200:
        traffic = response.json()
        print(f"Get Traffic by ID: {response.status_code} - {traffic}")

        # Decode and display the image if present
        if "image" in traffic and traffic["image"]:
            image_data = base64.b64decode(traffic["image"])
            image = Image.open(io.BytesIO(image_data))
            plt.imshow(image)
            plt.title("Uploaded Traffic Image")
            plt.axis("off")
            plt.show()

    return True


def test_error_cases():
    print("\n=== Testing Error Cases ===")
    
    # Test getting non-existent user
    response = requests.get(f"{BASE_URL}/users/nonexistent")
    print(f"Get Non-existent User: {response.status_code} - {response.json()}")
    
    # Test getting non-existent traffic data
    response = requests.get(f"{BASE_URL}/traffic/nonexistent")
    print(f"Get Non-existent Traffic: {response.status_code} - {response.json()}")

if __name__ == "__main__":
    try:
        print("Starting API tests...")
        
        # Check health first
        if not test_health():
            print("❌ Health check failed. Please check MongoDB connection.")
            exit(1)
        
        cleanup_test_data()
        
        if not test_users():
            print("❌ User tests failed")
            exit(1)
            
        if not test_traffic():
            print("❌ Traffic tests failed")
            exit(1)
            
        test_error_cases()
        print("\n✅ All tests completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to Flask server. Make sure it's running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
