# Job Platform

This document provides instructions for setting up, running, and developing the Job Platform application, which includes a Django backend API and a Vue.js frontend.

## 🚀 Project Overview

The Job Platform is a web application designed for managing job postings. It features:
- A backend API built with Django and Django Ninja for job and user management.
- A frontend interface built with Vue 3 and Vite.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

**Backend:**
- Python 3.8+
- pip
- virtualenv (recommended)

**Frontend:**
- Node.js (which includes npm)
- [VSCode](https://code.visualstudio.com/) (recommended)
- [Volar VSCode Extension](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (if using VSCode for Vue development, disable Vetur)

## ⚙️ Backend Setup & Usage

The backend is a Django application providing a RESTful API for job management.

### Installation

1.  **Navigate to the backend directory:**
    ```bash
    cd /home/eric/code/exercise/backend
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    *(On Windows, use `venv\Scripts\activate`)*

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Database Migration

Apply database migrations to set up the schema:
```bash
python3 manage.py migrate
```
*(Ensure your virtual environment is active)*

### Create Superuser (Required for login)

To access the Django admin interface, create a superuser:
```bash
python3 manage.py createsuperuser
```
*(Follow the prompts to set a username, email, and password)*

### Running the Development Server

Start the Django development server:
```bash
python3 manage.py runserver 8000
```
*(Ensure your virtual environment is active)*
The API will be accessible at `http://localhost:8000/api/`.

### Job Status Updates

Job statuses (e.g., from 'scheduled' to 'active', or 'active' to 'expired') are updated via a script.

**Manual Update:**
To manually trigger the job status update process:
```bash
# Ensure you are in the /home/eric/code/exercise/backend directory
# and the virtual environment is active.
./update_job_status.sh
```

**Log File:**
The job status update script logs its activity to:
`/home/eric/code/exercise/backend/job_status_scheduler.log`

You can also trigger this via an API endpoint if authenticated (see API Endpoints section).

## 🖥️ Frontend Setup & Usage

The frontend is a Vue.js application built with Vite.

### Recommended IDE Setup

- [VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (ensure Vetur is disabled if previously used).

### Type Support for `.vue` Imports in TypeScript

TypeScript cannot handle type information for `.vue` imports by default. The project uses `vue-tsc` for type checking instead of `tsc`. For editor support, Volar is necessary to make the TypeScript language service aware of `.vue` types.

### Customize Configuration

For more advanced configuration options, see the [Vite Configuration Reference](https://vite.dev/config/).

### Project Setup

1.  **Navigate to the frontend directory:**
    ```bash
    cd /home/eric/code/exercise/frontend
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

### Compile and Hot-Reload for Development

To run the frontend in development mode with hot-reloading:
```bash
npm run dev
```
The frontend application will typically be accessible at `http://localhost:5173/` (Vite will show the exact URL).

### Type-Check, Compile and Minify for Production

To build the frontend for production (includes type-checking, compilation, and minification):
```bash
npm run build
```
The production-ready files will be placed in the `dist` directory within `/home/eric/code/exercise/frontend`.

## 📚 API Endpoints

The backend provides the following API endpoints.

### Authentication Endpoints
| Method | Endpoint            | Description      | Auth Required |
|--------|---------------------|------------------|---------------|
| POST   | `/api/auth/login`   | User login       | ❌            |
| POST   | `/api/auth/refresh` | Refresh JWT      | ❌            |

### Job Management Endpoints
| Method | Endpoint                  | Description             | Auth Required |
|--------|---------------------------|-------------------------|---------------|
| POST   | `/api/jobs`               | Create a new job        | ✅            |
| GET    | `/api/jobs`               | Get list of jobs        | ✅            |
| GET    | `/api/jobs/{id}`          | Get job details         | ✅            |
| PUT    | `/api/jobs/{id}`          | Update a job            | ✅            |
| DELETE | `/api/jobs/{id}`          | Delete a job            | ✅            |
| POST   | `/api/jobs/update-status` | Manually update job statuses | ✅            |

### Query Parameters for `GET /api/jobs`

-   **Search**: `title`, `description`, `company_name`, `location`, `salary_range`
-   **Filter**: `status` (active, expired, scheduled), `required_skills` (comma-separated)
-   **Sort**: `order_by` (posting_date, -posting_date, expiration_date, -expiration_date)
-   **Pagination**: Automatic, 10 items per page.

**Example Queries:**
```
GET /api/jobs?title=engineer&status=active&order_by=-posting_date
GET /api/jobs?required_skills=Python,Django&location=Remote
```

## 🗄️ Data Model (Job)

Example structure of a Job object:
```json
{
  "id": 1,
  "title": "Software Engineer",
  "description": "Develop applications",
  "location": "Remote",
  "salary_range": "100k-150k USD",
  "company_name": "Tech Corp",
  "posting_date": "2025-01-01T00:00:00Z",
  "expiration_date": "2025-02-01T00:00:00Z",
  "required_skills": ["Python", "Django"],
  "is_active": true,
  "is_scheduled": false,
  "status": "Active" // (Active/Expired/Scheduled)
}
```

## 🔐 Authentication

The API uses JWT (JSON Web Token) for authentication.
1.  Log in via `/api/auth/login` to obtain an `access_token` and `refresh_token`.
2.  Include the `access_token` in the `Authorization` header for protected requests: `Authorization: Bearer <access_token>`.
3.  Use the `refresh_token` with `/api/auth/refresh` to get a new `access_token` when the current one expires.

## 🧪 Testing

### Backend Tests

**Run all backend tests:**
```bash
# Ensure you are in the /home/eric/code/exercise/backend directory
# and the virtual environment is active.
python3 -m pytest jobs/tests.py -v
python3 -m pytest user_auth/tests.py -v
```

**Test File Descriptions:**
-   `jobs/tests.py`: Core job management functionalities (CRUD, search, filter, pagination, scheduling).
-   `user_auth/tests.py`: User authentication functionalities (login, token refresh).

**Test Coverage Highlights:**
-   Authentication: Login, token refresh, unauthorized access.
-   Job CRUD: Create, Read, Update, Delete operations.
-   Search & Filtering: Various query parameter combinations.
-   Scheduled Jobs: Validation of scheduling logic.
-   Pagination: Verification of paginated results.
-   Error Handling: Testing for various error conditions.
-   Job Status Updates: Automated and manual status update logic.

### Frontend Tests
*(No automated frontend tests are currently configured in this project.)*

## 📖 API Documentation

Once the backend development server is running, API documentation is available at:
-   **Swagger UI**: `http://127.0.0.1:8000/api/docs`
-   **OpenAPI JSON**: `http://127.0.0.1:8000/api/openapi.json`

## 🛠️ Development Tools

### Django Admin Interface
Access the Django Admin for direct data management:
1.  Ensure you have created a superuser (see Backend Setup).
2.  Navigate to `http://127.0.0.1:8000/admin/` in your browser.

### Database Management (Django)
Common database commands:
```bash
# Ensure virtual environment is active and you are in /home/eric/code/exercise/backend
# Show migration status
python3 manage.py showmigrations

# Create new migration files (after model changes)
python3 manage.py makemigrations

# Apply migrations
python3 manage.py migrate
```

## 🚀 Deployment Considerations (Backend)

For deploying the backend to a production environment:
-   **Database**: Use a robust database like PostgreSQL instead of SQLite.
-   **WSGI Server**: Use a production-grade WSGI server like Gunicorn or uWSGI.
-   **Web Server/Proxy**: Place Nginx or Apache in front of the WSGI server to handle static files, SSL termination, and load balancing.
-   **Environment Variables**: Manage settings like `DJANGO_SETTINGS_MODULE`, `SECRET_KEY`, `DEBUG` status, and database credentials using environment variables.
    ```bash
    export DJANGO_SETTINGS_MODULE=job_platform.settings
    export SECRET_KEY='your-production-secret-key'
    export DEBUG=False
    # Add database connection variables
    ```
-   **HTTPS**: Enforce HTTPS for all communication.
-   **Logging**: Configure comprehensive logging for monitoring and debugging.
-   **Static Files**: Run `python3 manage.py collectstatic` and serve static files efficiently (e.g., via Nginx or a CDN).
-   **Allowed Hosts**: Configure `ALLOWED_HOSTS` in `settings.py` to include your production domain(s).