# AutoEye Backend API

Flask application for managing users and traffic data.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start MongoDB service

3. Run the application:
```bash
python app.py
```

## API Endpoints

### Users
- `POST /users` - Create a new user
- `GET /users` - Get all users
- `GET /users/<user_id>` - Get user by ID
- `PUT /users/<user_id>` - Update user
- `DELETE /users/<user_id>` - Delete user

### Traffic Data
- `POST /traffic` - Create traffic data
- `GET /traffic` - Get traffic data (supports location and status filters)
- `GET /traffic/<traffic_id>` - Get traffic data by ID
- `PUT /traffic/<traffic_id>` - Update traffic data
- `DELETE /traffic/<traffic_id>` - Delete traffic data

## Example Usage

Create user:
```bash
curl -X POST http://localhost:5000/users -H "Content-Type: application/json" -d '{"_id": "user123", "personal": {"name": "John Doe", "email": "john@example.com"}}'
```

Create traffic data:
```bash
curl -X POST http://localhost:5000/traffic -H "Content-Type: application/json" -d '{"_id": "traffic123", "location": "Location A", "vehicle_count": 50, "status": "HEAVY"}'
```

## Testing

### Manual Testing Steps

1. **Start MongoDB** (if using local installation):
```bash
mongod
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the Flask application**:
```bash
python app.py
```

4. **Run automated tests** (in another terminal):
```bash
python test_app.py
```

### Manual API Testing with curl

Test user creation:
```bash
curl -X POST http://localhost:5000/users \
  -H "Content-Type: application/json" \
  -d '{"_id": "user123", "personal": {"name": "John Doe", "email": "john@example.com"}}'
```

Test traffic data creation:
```bash
curl -X POST http://localhost:5000/traffic \
  -H "Content-Type: application/json" \
  -d '{"_id": "traffic123", "location": "Location A", "vehicle_count": 50, "status": "HEAVY"}'
```

Get all users:
```bash
curl http://localhost:5000/users
```

Get traffic data with filters:
```bash
curl "http://localhost:5000/traffic?location=Location A&status=HEAVY"
```