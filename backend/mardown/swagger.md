# AIoT-AutoEye Backend API

## Health Check

- **GET /health**
  - Response: `{ "status": "healthy", "database": "in-memory" | "connected" }`

## Users

- **POST /users**

  - Body: `{ "_id": "string", "personal": { "name": "string", "email": "string" } }`
  - Response: `{ "message": "User created", "id": "string" }`

- **GET /users**

  - Response: `[ { "_id": "...", "personal": { ... } } ]`

- **GET /users/<user_id>**

  - Response: `{ "_id": "...", "personal": { ... } }`

- **PUT /users/<user_id>**

  - Body: `{ "personal": { "name": "...", "email": "..." } }`
  - Response: `{ "message": "User updated" }`

- **DELETE /users/<user_id>**
  - Response: `{ "message": "User deleted" }`

## Traffic Data

- **POST /traffic**

  - Body: `{ "_id": "string", "location": "string", "vehicle_count": int, "status": "string", "timestamp": "ISO8601" }`
  - Response: `{ "message": "Traffic data created", "id": "string" }`

- **GET /traffic?location=...&status=...**

  - Response: `[ { "_id": "...", "location": "...", "vehicle_count": ..., "status": "...", "timestamp": "..." } ]`

- **GET /traffic/<traffic_id>**

  - Response: `{ "_id": "...", "location": "...", "vehicle_count": ..., "status": "...", "timestamp": "..." }`

- **PUT /traffic/<traffic_id>**

  - Body: `{ "location": "...", "vehicle_count": ..., "status": "..." }`
  - Response: `{ "message": "Traffic data updated" }`

- **DELETE /traffic/<traffic_id>**
  - Response: `{ "message": "Traffic data deleted" }`
