# FastAPI MongoDB Template

A production-ready FastAPI application with MongoDB integration, following clean architecture and best practices.

## Features

- FastAPI with async/await support
- MongoDB with Motor (async MongoDB driver)
- JWT Authentication
- Pydantic for data validation
- Environment variables configuration
- CORS support
- User management (register, login, update, delete)
- Clean project structure

## Prerequisites

- Python 3.8+
- MongoDB server (local or remote)
- pip (Python package manager)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd sandeepPRO
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Update the variables in `.env` as needed

## Running the Application

1. Start MongoDB server if not already running

2. Run the FastAPI application:
   ```bash
   uvicorn app.main:app --reload
   ```

3. The API will be available at `http://localhost:8000`

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
project/
├── app/
│   ├── api/                     # API routes
│   ├── core/                    # Core settings and security
│   ├── db/                      # Database models and session
│   ├── repository/              # Data access layer
│   ├── schemas/                 # Pydantic schemas
│   ├── services/                # Business logic
│   └── main.py                 # FastAPI app initialization
├── tests/                      # Test files
├── .env                        # Environment variables
└── requirements.txt            # Python dependencies
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/login/access-token` - Login and get access token
- `POST /api/v1/auth/register` - Register new user

### Users
- `GET /api/v1/users/me` - Get current user
- `GET /api/v1/users/{user_id}` - Get user by ID
- `PUT /api/v1/users/me` - Update current user
- `DELETE /api/v1/users/me` - Delete current user

## Environment Variables

See `.env.example` for all available environment variables.

## Testing

To run tests:
```bash
pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
