# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities

## Getting Started

1. Install the dependencies:

   ```
   pip install -r ../requirements.txt
   ```

2. Run the application:

   ```
   uvicorn app:app --reload
   ```

   Run these commands from the `src` directory. On first startup, the app creates
   a SQLite database at `src/activities.sqlite3` and seeds it with the existing
   activities and participants. The database file is not tracked by Git.

   To store the database elsewhere, set `ACTIVITY_DATABASE_PATH` before starting
   the app:

   ```
   ACTIVITY_DATABASE_PATH=/path/to/activities.sqlite3 uvicorn app:app --reload
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                              | Description                                        |
| ------ | --------------------------------------------------------------------- | -------------------------------------------------- |
| GET    | `/activities`                                                         | Get all activities and their participants          |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu`     | Sign up for an activity                            |
| DELETE | `/activities/{activity_name}/unregister?email=student@mergington.edu` | Unregister a student from an activity              |

## Data Model

The SQLite database contains:

1. **Activities** - Activity name is the identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
2. **Enrollments** - Activity name and student email identify each signup
3. **Student accounts** - Student details and a password-hash field
4. **Service-hour entries** - Student, date, hours, description, review status,
   and optional review details

Activities and enrollments are seeded with the existing sample data only when
the database is empty. Later application starts use the saved database and do
not overwrite its contents. The student-account and service-hour tables provide
persistent storage for those workflows as they are implemented.
