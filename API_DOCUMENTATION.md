# Nulinks API Documentation

The Nulinks API provides programmatic access to post Fopnu links for automation purposes. This allows command-line tools and bots to post links without using the web interface.

## Authentication

The API uses token-based authentication. You need to obtain an API token by logging in with your username and password.

### Getting an API Token

```bash
curl -X POST "http://your-server/api/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

Response:
```json
{
    "token": "your_api_token_here",
    "user_id": 123,
    "username": "your_username"
}
```

### Using the Token

Include the token in the Authorization header for all subsequent requests:

```bash
curl -H "Authorization: Token your_api_token_here" "http://your-server/api/links/"
```

## API Endpoints

### 1. Get API Information
- **URL**: `/api/info/`
- **Method**: `GET`
- **Authentication**: Not required
- **Description**: Get API documentation and usage information

```bash
curl "http://your-server/api/info/"
```

### 2. Login
- **URL**: `/api/auth/login/`
- **Method**: `POST`
- **Authentication**: Not required
- **Description**: Login and get API token

```bash
curl -X POST "http://your-server/api/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'
```

### 3. List Categories
- **URL**: `/api/categories/`
- **Method**: `GET`
- **Authentication**: Required
- **Description**: Get list of available categories

```bash
curl -H "Authorization: Token your_token" "http://your-server/api/categories/"
```

### 4. List User's Links
- **URL**: `/api/links/`
- **Method**: `GET`
- **Authentication**: Required
- **Description**: Get all links posted by the authenticated user

```bash
curl -H "Authorization: Token your_token" "http://your-server/api/links/"
```

### 5. Post Single Link
- **URL**: `/api/links/`
- **Method**: `POST`
- **Authentication**: Required
- **Description**: Post a single Fopnu link

```bash
curl -X POST "http://your-server/api/links/" \
  -H "Authorization: Token your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "fopnu://file:/Movies/Action/Sample%20Movie.mkv",
    "category_id": 1
  }'
```

**Parameters**:
- `location` (required): The Fopnu link URL
- `category_id` (optional): ID of the category to assign to the link

### 6. Post Multiple Links (Bulk)
- **URL**: `/api/links/bulk/`
- **Method**: `POST`
- **Authentication**: Required
- **Description**: Post multiple Fopnu links at once (up to 100 links)

```bash
curl -X POST "http://your-server/api/links/bulk/" \
  -H "Authorization: Token your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "links": [
      "fopnu://file:/Music/Rock/Song1.mp3",
      "fopnu://file:/Music/Rock/Song2.mp3",
      "fopnu://file:/Music/Rock/Song3.mp3"
    ],
    "category_id": 2
  }'
```

**Parameters**:
- `links` (required): Array of Fopnu link URLs (max 100)
- `category_id` (optional): ID of the category to assign to all links

## Example Usage Scripts

### Bash Script for Posting Links

```bash
#!/bin/bash

SERVER="http://localhost:8001"
USERNAME="your_username"
PASSWORD="your_password"

# Get API token
TOKEN=$(curl -s -X POST "$SERVER/api/auth/login/" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"$USERNAME\", \"password\": \"$PASSWORD\"}" | \
  python -c "import sys, json; print(json.load(sys.stdin)['token'])")

echo "Got token: $TOKEN"

# Post a single link
curl -X POST "$SERVER/api/links/" \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"location": "fopnu://file:/test/example.txt"}'

# Post multiple links
curl -X POST "$SERVER/api/links/bulk/" \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "links": [
      "fopnu://file:/Movies/movie1.mkv",
      "fopnu://file:/Movies/movie2.mkv",
      "fopnu://file:/Movies/movie3.mkv"
    ],
    "category_id": 1
  }'
```

### Python Script for Posting Links

```python
#!/usr/bin/env python3
import requests
import json

SERVER = "http://localhost:8001"
USERNAME = "your_username"
PASSWORD = "your_password"

# Get API token
login_data = {"username": USERNAME, "password": PASSWORD}
response = requests.post(f"{SERVER}/api/auth/login/", json=login_data)
token = response.json()["token"]

headers = {"Authorization": f"Token {token}"}

# Post a single link
link_data = {
    "location": "fopnu://file:/test/example.txt",
    "category_id": 1
}
response = requests.post(f"{SERVER}/api/links/", json=link_data, headers=headers)
print("Single link posted:", response.json())

# Post multiple links
bulk_data = {
    "links": [
        "fopnu://file:/Movies/movie1.mkv",
        "fopnu://file:/Movies/movie2.mkv", 
        "fopnu://file:/Movies/movie3.mkv"
    ],
    "category_id": 1
}
response = requests.post(f"{SERVER}/api/links/bulk/", json=bulk_data, headers=headers)
print("Bulk links posted:", response.json())
```

## Error Responses

The API returns appropriate HTTP status codes and error messages:

- `400 Bad Request`: Invalid input data
- `401 Unauthorized`: Missing or invalid authentication
- `404 Not Found`: Resource not found

Example error response:
```json
{
    "detail": "Authentication credentials were not provided."
}
```

## Rate Limits

- Bulk operations are limited to 100 links per request
- No other rate limits are currently enforced

## Name Extraction

The API automatically extracts file names from Fopnu links:
- `fopnu://file:/Movies/Action/Sample%20Movie.mkv` → `Sample Movie.mkv`
- `fopnu://user:/some/user/path` → `path`
- Regular URLs are used as-is for the name field