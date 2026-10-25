import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import app


class PersistenceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "test.sqlite3"
        self.database_path_patch = patch.object(app, "DATABASE_PATH", self.database_path)
        self.database_path_patch.start()
        app.initialize_database()

    def tearDown(self):
        self.database_path_patch.stop()
        self.temp_dir.cleanup()

    def test_activity_enrollments_and_api_behavior_survive_restart(self):
        activities = app.get_activities()
        self.assertIn("Chess Club", activities)
        self.assertEqual(
            activities["Chess Club"]["participants"],
            ["michael@mergington.edu", "daniel@mergington.edu"],
        )

        email = "new.student@mergington.edu"
        self.assertEqual(
            app.signup_for_activity("Chess Club", email),
            {"message": f"Signed up {email} for Chess Club"},
        )
        app.initialize_database()
        self.assertIn(email, app.get_activities()["Chess Club"]["participants"])

        with self.assertRaises(HTTPException) as duplicate:
            app.signup_for_activity("Chess Club", email)
        self.assertEqual(duplicate.exception.status_code, 400)

        self.assertEqual(
            app.unregister_from_activity("Chess Club", email),
            {"message": f"Unregistered {email} from Chess Club"},
        )
        app.initialize_database()
        self.assertNotIn(email, app.get_activities()["Chess Club"]["participants"])

    def test_student_accounts_and_service_hour_reviews_are_persistent(self):
        with app.database_connection() as connection:
            connection.execute(
                """
                INSERT INTO student_accounts (email, name, grade, password_hash)
                VALUES (?, ?, ?, ?)
                """,
                (
                    "student@mergington.edu",
                    "Student",
                    "11",
                    "test-password-hash",
                ),
            )
            connection.execute(
                """
                INSERT INTO service_hour_entries
                    (student_email, service_date, hours, description, status,
                     reviewed_by, reviewed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "student@mergington.edu",
                    "2026-10-24",
                    2.5,
                    "Community cleanup",
                    "approved",
                    "teacher@mergington.edu",
                    "2026-10-25T10:00:00",
                ),
            )

        app.initialize_database()

        with app.database_connection() as connection:
            account = connection.execute(
                "SELECT email, password_hash FROM student_accounts"
            ).fetchone()
            entry = connection.execute(
                """
                SELECT student_email, hours, status, reviewed_by
                FROM service_hour_entries
                """
            ).fetchone()

        self.assertEqual(account["email"], "student@mergington.edu")
        self.assertEqual(account["password_hash"], "test-password-hash")
        self.assertEqual(entry["student_email"], "student@mergington.edu")
        self.assertEqual(entry["hours"], 2.5)
        self.assertEqual(entry["status"], "approved")
        self.assertEqual(entry["reviewed_by"], "teacher@mergington.edu")


if __name__ == "__main__":
    unittest.main()
