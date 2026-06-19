# GitHub Copilot Agent Instructions

This is a GitHub Skills exercise project featuring a simple FastAPI application for managing high school extracurricular activities.

## Quick Start

### Installation & Running
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python src/app.py

# Run tests
pytest
```

The API runs on `http://localhost:8000` with interactive documentation at `/docs`.

## Architecture

### Project Structure
- **`src/app.py`** - Main FastAPI application with two endpoints:
  - `GET /activities` - Retrieve all activities with participant counts
  - `POST /activities/{activity_name}/signup?email=...` - Sign up a student
- **`src/static/`** - Frontend assets (HTML, CSS, JavaScript)
- **`tests/`** - pytest test suite

### Core Patterns
1. **In-Memory Database**: Activities and students stored as Python dictionaries. Data resets on server restart.
2. **Data Model**:
   - Activities identified by name (not ID)
   - Each activity has: description, schedule, max_participants, participants list
   - Students identified by email
3. **API Design**: RESTful endpoints with JSON responses and HTTP error codes

## Development Conventions

### When Adding Features
- **Validation**: Always validate max_participants limit before accepting signups
- **Error Handling**: Use FastAPI's `HTTPException` with appropriate status codes
- **Data Integrity**: Prevent duplicate signups (check if email already in participants list)
- **Email Format**: Use `.edu` domain convention for all student emails

### Frontend Integration
- Static files served from `/static/`
- API responses used by JavaScript in `static/app.js`
- Ensure API changes are reflected in the frontend UI

### Testing
- Use pytest for all tests
- Tests can be run with `pytest` or `python -m pytest`
- Configuration in `pytest.ini` sets Python path

## Common Tasks & Patterns

### Adding a New Endpoint
1. Define the endpoint in `app.py` using FastAPI decorators (`@app.get()`, `@app.post()`)
2. Validate inputs and check activity/participant existence
3. Return appropriate HTTP status codes (200 OK, 400 Bad Request, 404 Not Found, etc.)
4. Write corresponding tests in `tests/`

### Modifying Activities Data
- Activities are stored as a dictionary in module scope
- To add/modify activities, update the `activities` dict in `app.py`
- Changes persist only during current session (in-memory storage)

### Error Responses
- Use `raise HTTPException(status_code=..., detail="...")`
- Common codes: 400 (bad request), 404 (not found), 409 (conflict/duplicate)

## Potential Pitfalls

⚠️ **In-Memory Storage**: All data is lost when the server restarts. This is intentional for this simple exercise.

⚠️ **Duplicate Signups**: Current implementation may not prevent the same student from signing up multiple times to the same activity—verify and add validation if needed.

⚠️ **Case Sensitivity**: Activity names are case-sensitive in the current implementation. Be consistent when referencing activities.

⚠️ **Import Path**: When running scripts or tests, ensure the Python path includes the project root (handled by pytest.ini).

## Documentation & Links

See [README.md](README.md) and [src/README.md](src/README.md) for detailed project information and API endpoint documentation.
