# StrettoNotes API

FastAPI backend for StrettoNotes - a voice-first practice journal for musicians.

## Quick Start

### Local Development

1. **Clone and setup:**
```bash
git clone [your-repo-url]
cd stretto-notes-api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your MongoDB Atlas connection string
```

3. **Run locally:**
```bash
uvicorn main:app --reload
```

Visit http://localhost:8000/docs for interactive API documentation.

### Deploy to Railway

1. **Push to GitHub:**
```bash
git add .
git commit -m "Initial FastAPI backend"
git push origin main
```

2. **In Railway:**
- Connect your GitHub repo
- Railway will auto-detect Python and deploy
- Add environment variables in Railway dashboard:
  - `MONGODB_URL` - Your MongoDB Atlas connection string
  - `DATABASE_NAME` - stretto_notes (or your preference)
  - `SECRET_KEY` - Generate with: `openssl rand -hex 32`

3. **Railway will provide your API URL:**
- Something like: `https://your-app.railway.app`

## API Endpoints

### Authentication
- `POST /register` - Create new user
- `POST /token` - Login (returns JWT token)
- `GET /me` - Get current user info

### Protected Endpoints (require token)
- `GET /sessions` - Get user's sessions
- `POST /sessions` - Create session
- `GET /sessions/{id}` - Get specific session
- `PUT /sessions/{id}` - Update session

- `GET /practice-items` - Get user's practice items
- `POST /practice-items` - Create practice item

- `GET /journeys` - Get user's journeys
- `POST /journeys` - Create journey
- `PUT /journeys/{id}` - Update journey

## Testing the API

### Register a user:
```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass","full_name":"Test User"}'
```

### Login:
```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=testpass"
```

### Use the token:
```bash
curl -X GET "http://localhost:8000/sessions" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Flutter Integration

Update your Flutter app to use the API:

```dart
class ApiService {
  final String baseUrl = 'https://your-app.railway.app';
  String? _token;
  
  Future<void> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/token'),
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      body: {'username': email, 'password': password},
    );
    
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      _token = data['access_token'];
    }
  }
  
  Future<List<Session>> getSessions() async {
    final response = await http.get(
      Uri.parse('$baseUrl/sessions'),
      headers: {'Authorization': 'Bearer $_token'},
    );
    // Parse response...
  }
}
```

## Next Steps

1. Add more validation to Pydantic models
2. Implement pagination for list endpoints
3. Add filtering/search capabilities
4. Set up proper CORS for production
5. Add rate limiting
6. Implement refresh tokens
7. Add logging and monitoring

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| MONGODB_URL | MongoDB connection string | Yes |
| DATABASE_NAME | Database name | Yes |
| SECRET_KEY | JWT signing key | Yes |
| PORT | Server port (default: 8000) | No |
