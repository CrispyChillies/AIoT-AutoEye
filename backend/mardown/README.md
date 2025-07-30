# Save the README markdown content into a file

markdown_content = """
# 🚦 AutoEye API - Flask + MongoDB CRUD

This project provides a simple RESTful API for managing **user data** and **traffic monitoring data**, built using **Flask** and **MongoDB**.

---

## 📦 Features

- MongoDB-based CRUD operations
- Two collections:
  - `/users`: Manage user information
  - `/traffic`: Store traffic monitoring data
- Health check endpoint (`/health`)
- Error handling and validation
- Environment configuration via `.env`

---

## ⚙️ Environment Setup

### 1. Install dependencies

```bash
pip install flask pymongo python-dotenv
```

### 2. Setup `.env`

Create a `.env` file:

```env
MONGO_URI=mongodb://localhost:27017/
```

---

## 🚀 Running the App

```bash
python app.py
```

Server runs at: `http://localhost:5000`

---

## 📁 MongoDB Collections

- **Database:** `autoeye_db`
- **Collections:**
  - `users`
  - `traffic_data`

---

## 🧑‍💼 `/users` Endpoints

### 🔹 Create a user

**POST** `/users`

```json
{
  "_id": "user001",
  "personal": {
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

- Requires `_id`, `name`, and `email`

---

### 🔹 Get all users

**GET** `/users`

Returns a list of all users.

---

### 🔹 Get user by ID

**GET** `/users/<user_id>`

Returns a single user by ID.

---

### 🔹 Update user

**PUT** `/users/<user_id>`

```json
{
  "personal": {
    "name": "Jane Smith",
    "email": "jane@example.com"
  }
}
```

---

### 🔹 Delete user

**DELETE** `/users/<user_id>`

Deletes the user with the given ID.

---

## 🚗 `/traffic` Endpoints

### 🔹 Create traffic data

**POST** `/traffic`

```json
{
  "_id": "traffic001",
  "timestamp": "2024-07-10T10:00:00Z",
  "location": "District 1",
  "vehicle_count": 150,
  "status": "normal"
}
```

- `_id` is required
- `timestamp` is optional (defaults to current UTC time)

---

### 🔹 Get traffic data

**GET** `/traffic?location=District%201&status=normal`

- Optional query params: `location`, `status`

---

### 🔹 Get traffic data by ID

**GET** `/traffic/<traffic_id>`

Returns a single traffic record.

---

### 🔹 Update traffic data

**PUT** `/traffic/<traffic_id>`

```json
{
  "location": "District 2",
  "vehicle_count": 120,
  "status": "heavy"
}
```

---

### 🔹 Delete traffic data

**DELETE** `/traffic/<traffic_id>`

Deletes the traffic record with the given ID.

---

## ❤️ Health Check

**GET** `/health`

Returns MongoDB connection status.

```json
{
  "status": "healthy",
  "database": "connected"
}
```
