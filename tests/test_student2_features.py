"""Run: python -m unittest discover -s tests -v"""
import tempfile
import unittest
from pathlib import Path

import database

# Avoid creating or modifying the project's own expenses.db on app import.
_import_directory = tempfile.TemporaryDirectory()
database.DATABASE_PATH = Path(_import_directory.name) / "import.db"

from app import app  # noqa: E402


class ExpenseFeatureTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        database.DATABASE_PATH = Path(self.directory.name) / "test.db"
        database.init_db()
        app.config.update(TESTING=True)
        self.client = app.test_client()
        connection = database.get_db_connection()
        self.category = connection.execute(
            "SELECT id FROM categories WHERE is_archived = 0 LIMIT 1"
        ).fetchone()["id"]
        connection.execute(
            """INSERT INTO expenses (title, amount, category_id, expense_date, notes)
               VALUES (?, ?, ?, ?, ?)""",
            ("Train pass", 120.0, self.category, "2026-11-14", "Morning travel"),
        )
        connection.commit()
        self.expense_id = connection.execute(
            "SELECT id FROM expenses WHERE title = ?", ("Train pass",)
        ).fetchone()["id"]
        connection.close()

    def tearDown(self):
        self.directory.cleanup()

    def fetch_expense(self):
        connection = database.get_db_connection()
        expense = connection.execute(
            "SELECT * FROM expenses WHERE id = ?", (self.expense_id,)
        ).fetchone()
        connection.close()
        return expense

    def test_edit_button_opens_prefilled_form(self):
        listing = self.client.get("/expenses")
        self.assertEqual(listing.status_code, 200)
        self.assertIn(f"/expenses/{self.expense_id}/edit".encode(), listing.data)
        response = self.client.get(f"/expenses/{self.expense_id}/edit")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Train pass", response.data)
        self.assertIn(b"Morning travel", response.data)

    def test_edit_updates_existing_record(self):
        response = self.client.post(
            f"/expenses/{self.expense_id}/edit",
            data={
                "title": "Updated train pass",
                "amount": "249.50",
                "category_id": str(self.category),
                "expense_date": "2026-11-13",
                "notes": "Afternoon",
            },
        )
        self.assertEqual(response.status_code, 302)
        expense = self.fetch_expense()
        self.assertEqual(expense["title"], "Updated train pass")
        self.assertEqual(expense["amount"], 249.50)
        self.assertEqual(expense["expense_date"], "2026-11-13")
        self.assertEqual(expense["notes"], "Afternoon")
        connection = database.get_db_connection()
        self.assertEqual(connection.execute("SELECT COUNT(*) FROM expenses").fetchone()[0], 1)
        connection.close()

    def test_invalid_edit_keeps_original_data(self):
        response = self.client.post(
            f"/expenses/{self.expense_id}/edit",
            data={
                "title": "Bad amount", "amount": "-5", "category_id": str(self.category),
                "expense_date": "2026-11-31", "notes": "",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.fetch_expense()["title"], "Train pass")

    def test_deleted_expense_cannot_be_edited(self):
        self.client.post(f"/expenses/{self.expense_id}/delete")
        response = self.client.get(f"/expenses/{self.expense_id}/edit")
        self.assertEqual(response.status_code, 302)

    def test_restore_all_restores_only_deleted_expenses(self):
        connection = database.get_db_connection()
        connection.execute(
            """INSERT INTO expenses (title, amount, category_id, expense_date, is_deleted, deleted_at)
               VALUES ('Taxi', 90, ?, '2026-11-14', 1, CURRENT_TIMESTAMP)""",
            (self.category,),
        )
        connection.commit()
        connection.close()
        self.client.post(f"/expenses/{self.expense_id}/delete")
        page = self.client.get("/recycle-bin")
        self.assertIn(b"Restore All", page.data)
        self.assertIn(b"/expenses/restore-all", page.data)
        response = self.client.post("/expenses/restore-all")
        self.assertEqual(response.status_code, 302)
        connection = database.get_db_connection()
        self.assertEqual(connection.execute("SELECT COUNT(*) FROM expenses WHERE is_deleted = 1").fetchone()[0], 0)
        self.assertEqual(connection.execute("SELECT COUNT(*) FROM expenses WHERE deleted_at IS NOT NULL").fetchone()[0], 0)
        connection.close()
        self.assertNotIn(b"Restore All", self.client.get("/recycle-bin").data)

    def test_restore_all_does_not_delete_or_duplicate_data(self):
        self.client.post("/expenses/restore-all")
        self.assertEqual(self.fetch_expense()["title"], "Train pass")
        connection = database.get_db_connection()
        self.assertEqual(connection.execute("SELECT COUNT(*) FROM expenses").fetchone()[0], 1)
        connection.close()


if __name__ == "__main__":
    unittest.main()
