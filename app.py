from datetime import date

import csv
from io import StringIO
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    make_response,
)

from database import get_db_connection, init_db

app = Flask(__name__) # Initialized by ravii
app.secret_key = "dev-key-change-before-deployment"

init_db()


@app.route("/")
def dashboard():
    connection = get_db_connection()

    today = date.today()
    today_text = today.isoformat()
    current_month = today.strftime("%Y-%m")

    # Get active categories for the dashboard form.
    categories = connection.execute("""
        SELECT id, name, icon
        FROM categories
        WHERE is_archived = 0
        ORDER BY name
    """).fetchall()

    # Get dashboard statistics.
    stats = connection.execute(
        """
        SELECT
            COALESCE(SUM(amount), 0) AS total_expenses,
            COALESCE(SUM(
                CASE
                    WHEN strftime('%Y-%m', expense_date) = ?
                    THEN amount
                    ELSE 0
                END
            ), 0) AS monthly_expenses,
            COUNT(*) AS transaction_count
        FROM expenses
        WHERE is_deleted = 0
    """,
        (current_month,),
    ).fetchone()

    # Build the last 6 calendar months.
    months = []

    for offset in range(5, -1, -1):
        month_index = today.year * 12 + today.month - 1 - offset
        year = month_index // 12
        month = month_index % 12 + 1
        months.append(date(year, month, 1))

    start_date = months[0].isoformat()

    if today.month == 12:
        end_date = date(today.year + 1, 1, 1).isoformat()
    else:
        end_date = date(today.year, today.month + 1, 1).isoformat()

    # Get monthly spending from SQLite.
    monthly_rows = connection.execute(
        """
        SELECT
            strftime('%Y-%m', expense_date) AS month,
            SUM(amount) AS total
        FROM expenses
        WHERE is_deleted = 0
          AND expense_date >= ?
          AND expense_date < ?
        GROUP BY strftime('%Y-%m', expense_date)
    """,
        (start_date, end_date),
    ).fetchall()

    monthly_totals = {row["month"]: row["total"] for row in monthly_rows}

    # Include months with zero spending.
    monthly_spending = [
        {
            "label": month.strftime("%b"),
            "amount": monthly_totals.get(month.strftime("%Y-%m"), 0) or 0,
        }
        for month in months
    ]

    # Get spending grouped by category.
    category_rows = connection.execute("""
        SELECT
            COALESCE(c.name, 'Uncategorized') AS category_name,
            COALESCE(c.icon, ' ') AS category_icon,
            SUM(e.amount) AS total
        FROM expenses AS e
        LEFT JOIN categories AS c
            ON e.category_id = c.id
        WHERE e.is_deleted = 0
        GROUP BY e.category_id, c.name, c.icon
        ORDER BY total DESC
    """).fetchall()

    category_spending = [
        {
            "name": row["category_name"],
            "icon": row["category_icon"],
            "amount": row["total"],
        }
        for row in category_rows
    ]

    connection.close()

    return render_template(
        "index.html",
        categories=categories,
        today=today_text,
        total_expenses=stats["total_expenses"],
        monthly_expenses=stats["monthly_expenses"],
        transaction_count=stats["transaction_count"],
        monthly_spending=monthly_spending,
        category_spending=category_spending,
    )


@app.route("/expenses")
def expense_list():
    connection = get_db_connection()

    expenses = connection.execute("""
        SELECT
            e.id,
            e.title,
            e.amount,
            e.expense_date,
            e.notes,
            c.name AS category_name,
            c.icon AS category_icon
        FROM expenses AS e
        LEFT JOIN categories AS c
            ON e.category_id = c.id
        WHERE e.is_deleted = 0
        ORDER BY e.expense_date DESC, e.id DESC
    """).fetchall()

    # Get expense totals grouped by category.
    category_summary = connection.execute("""
        SELECT
            COALESCE(c.name, 'Uncategorized') AS category_name,
            COALESCE(c.icon, '📦') AS category_icon,
            SUM(e.amount) AS total
        FROM expenses AS e
        LEFT JOIN categories AS c
            ON e.category_id = c.id
        WHERE e.is_deleted = 0
        GROUP BY e.category_id, c.name, c.icon
        ORDER BY total DESC
    """).fetchall()

    # Get total expenses for each month.
    monthly_summary = connection.execute("""
        SELECT
            strftime('%Y-%m', expense_date) AS month_key,
            SUM(amount) AS total
        FROM expenses
        WHERE is_deleted = 0
        GROUP BY strftime('%Y-%m', expense_date)
        ORDER BY month_key DESC
    """).fetchall()

    # Get category totals separately for each month.
    monthly_category_summary = connection.execute("""
        SELECT
            strftime('%Y-%m', e.expense_date) AS month_key,
            COALESCE(c.name, 'Uncategorized') AS category_name,
            COALESCE(c.icon, '📦') AS category_icon,
            SUM(e.amount) AS total
        FROM expenses AS e
        LEFT JOIN categories AS c
            ON e.category_id = c.id
        WHERE e.is_deleted = 0
        GROUP BY
            strftime('%Y-%m', e.expense_date),
            e.category_id,
            c.name,
            c.icon
        ORDER BY month_key DESC, total DESC
    """).fetchall()

    # Prepare readable month names for the HTML template.
    monthly_summary = [
        {
            "month_key": row["month_key"],
            "month": date.fromisoformat(row["month_key"] + "-01").strftime("%B %Y"),
            "total": row["total"],
        }
        for row in monthly_summary
    ]

    monthly_category_summary = [
        {
            "month_key": row["month_key"],
            "month": date.fromisoformat(row["month_key"] + "-01").strftime("%B %Y"),
            "category_name": row["category_name"],
            "category_icon": row["category_icon"],
            "total": row["total"],
        }
        for row in monthly_category_summary
    ]

    connection.close()

    return render_template(
        "expenses_list.html",
        expenses=expenses,
        category_summary=category_summary,
        monthly_summary=monthly_summary,
        monthly_category_summary=monthly_category_summary,
    )


@app.route("/add-expense", methods=["GET", "POST"])
def add_expense():
    connection = get_db_connection()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        amount_text = request.form.get("amount", "").strip()
        category_id = request.form.get("category_id", "").strip()
        expense_date = request.form.get("expense_date", "").strip()
        notes = request.form.get("notes", "").strip()
        new_category_name = request.form.get("new_category_name", "").strip()
        new_category_icon = request.form.get("new_category_icon", " ").strip() or ""
        try:
            amount = float(amount_text)
        except ValueError:
            amount = 0

        # Validate expense details before creating a category.
        if not title or amount <= 0 or not expense_date:
            flash("Enter a valid title, amount and date.", "error")
            connection.close()
            return redirect(url_for("dashboard"))

        # Create a category only when a new name is provided.
        if new_category_name:
            category = connection.execute(
                """
                SELECT id FROM categories
                WHERE name = ? COLLATE NOCASE AND is_archived = 0
                """,
                (new_category_name,),
            ).fetchone()

            if category:
                category_id = category["id"]
            else:
                cursor = connection.execute(
                    """
                    INSERT INTO categories (name, icon)
                    VALUES (?, ?)
                    """,
                    (new_category_name, new_category_icon),
                )
                category_id = cursor.lastrowid

        # Check the selected or newly created category.
        category = connection.execute(
            """
            SELECT id FROM categories
            WHERE id = ? AND is_archived = 0
            """,
            (category_id,),
        ).fetchone()

        if not category:
            flash(
                "Please select an existing category or enter a new category name.",
                "error",
            )
            connection.close()
            return redirect(url_for("dashboard"))

        connection.execute(
            """
            INSERT INTO expenses
                (title, amount, category_id, expense_date, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (title, amount, category["id"], expense_date, notes),
        )

        connection.commit()
        connection.close()

        flash("Expense added successfully!", "success")
        return redirect(url_for("expense_list"))

    categories = connection.execute(
        "SELECT id, name, icon FROM categories " "WHERE is_archived = 0 ORDER BY name"
    ).fetchall()

    connection.close()

    return render_template(
        "add_expense.html", categories=categories, today=date.today().isoformat()
    )


@app.route("/create-category", methods=["POST"])
def create_category():
    name = request.form.get("name", "").strip()
    icon = request.form.get("icon", "").strip() or ""

    if not name:
        flash("Please enter a category name.", "error")
        return redirect(url_for("dashboard"))

    connection = get_db_connection()

    existing = connection.execute(
        "SELECT id FROM categories WHERE name = ? AND is_archived = 0", (name,)
    ).fetchone()

    if existing:
        connection.close()
        flash("This category already exists.", "error")
        return redirect(url_for("dashboard"))

    connection.execute(
        "INSERT INTO categories (name, icon) VALUES (?, ?)", (name, icon)
    )

    connection.commit()
    connection.close()

    flash("Category created successfully!", "success")
    return redirect(url_for("dashboard"))


# from datetime import date, datetime
@app.route("/categories")
def categories():
    connection = get_db_connection()

    active_categories = connection.execute("""
        SELECT id, name, icon
        FROM categories
        WHERE is_archived = 0
        ORDER BY name
    """).fetchall()

    archived_categories = connection.execute("""
        SELECT id, name, icon
        FROM categories
        WHERE is_archived = 1
        ORDER BY name
    """).fetchall()

    connection.close()

    return render_template(
        "categories.html",
        active_categories=active_categories,
        archived_categories=archived_categories,
    )


@app.route("/categories/<int:category_id>/archive", methods=["POST"])
def archive_category(category_id):
    connection = get_db_connection()

    connection.execute(
        "UPDATE categories SET is_archived = 1 WHERE id = ?", (category_id,)
    )

    connection.commit()
    connection.close()

    flash("Category archived successfully.", "success")
    return redirect(url_for("categories"))


@app.route("/categories/<int:category_id>/restore", methods=["POST"])
def restore_category(category_id):
    connection = get_db_connection()

    connection.execute(
        "UPDATE categories SET is_archived = 0 WHERE id = ?", (category_id,)
    )

    connection.commit()
    connection.close()

    flash("Category restored successfully.", "success")
    return redirect(url_for("categories"))


@app.route("/recycle-bin")
def recycle_bin():
    connection = get_db_connection()

    deleted_expenses = connection.execute("""
        SELECT
            e.id,
            e.title,
            e.amount,
            e.expense_date,
            e.deleted_at,
            c.name AS category_name,
            c.icon AS category_icon
        FROM expenses AS e
        LEFT JOIN categories AS c
            ON e.category_id = c.id
        WHERE e.is_deleted = 1
        ORDER BY e.deleted_at DESC, e.id DESC
    """).fetchall()

    connection.close()

    return render_template("recycle_bin.html", deleted_expenses=deleted_expenses)


@app.route("/expenses/<int:expense_id>/delete", methods=["POST"])
def delete_expense(expense_id):
    connection = get_db_connection()

    connection.execute(
        """
        UPDATE expenses
        SET is_deleted = 1,
            deleted_at = CURRENT_TIMESTAMP
        WHERE id = ? AND is_deleted = 0
    """,
        (expense_id,),
    )

    connection.commit()
    connection.close()

    flash("Expense moved to Recycle Bin.", "success")
    return redirect(url_for("expense_list"))


@app.route("/expenses/delete-all", methods=["POST"])
def delete_all_expenses():
    connection = get_db_connection()

    connection.execute("""
        UPDATE expenses
        SET is_deleted = 1,
            deleted_at = CURRENT_TIMESTAMP
        WHERE is_deleted = 0
    """)

    connection.commit()
    connection.close()

    flash("All expenses moved to Recycle Bin.", "success")
    return redirect(url_for("expense_list"))


@app.route("/expenses/<int:expense_id>/restore", methods=["POST"])
def restore_expense(expense_id):
    connection = get_db_connection()

    connection.execute(
        """
        UPDATE expenses
        SET is_deleted = 0,
            deleted_at = NULL
        WHERE id = ? AND is_deleted = 1
    """,
        (expense_id,),
    )

    connection.commit()
    connection.close()

    flash("Expense restored successfully.", "success")
    return redirect(url_for("recycle_bin"))


@app.route("/expenses/<int:expense_id>/delete-permanently", methods=["POST"])
def permanently_delete_expense(expense_id):
    connection = get_db_connection()

    connection.execute(
        """
        DELETE FROM expenses
        WHERE id = ? AND is_deleted = 1
    """,
        (expense_id,),
    )

    connection.commit()
    connection.close()

    flash("Expense permanently deleted.", "success")
    return redirect(url_for("recycle_bin"))


@app.route("/reports")
def reports():
    connection = get_db_connection()

    # Get overall expense statistics.
    summary = connection.execute("""
        SELECT
            COUNT(*) AS total_count,
            COALESCE(SUM(amount), 0) AS total_amount,
            COALESCE(AVG(amount), 0) AS average_amount
        FROM expenses
        WHERE is_deleted = 0
    """).fetchone()

    # Get spending totals for each category.
    category_summary = connection.execute("""
        SELECT
            COALESCE(c.name, 'Uncategorized') AS category_name,
            COALESCE(c.icon, '📦') AS category_icon,
            SUM(e.amount) AS total
        FROM expenses AS e
        LEFT JOIN categories AS c
            ON e.category_id = c.id
        WHERE e.is_deleted = 0
        GROUP BY e.category_id, c.name, c.icon
        ORDER BY total DESC
    """).fetchall()

    # Get the latest expenses.
    recent_expenses = connection.execute("""
        SELECT
            e.title,
            e.amount,
            e.expense_date,
            e.notes,
            COALESCE(c.name, 'Uncategorized') AS category_name
        FROM expenses AS e
        LEFT JOIN categories AS c
            ON e.category_id = c.id
        WHERE e.is_deleted = 0
        ORDER BY e.expense_date DESC, e.id DESC
        LIMIT 10
    """).fetchall()

    connection.close()

    return render_template(
        "reports.html",
        summary=summary,
        category_summary=category_summary,
        recent_expenses=recent_expenses,
    )


@app.route("/reports/export/csv")
def export_expenses_csv():
    connection = get_db_connection()

    expenses = connection.execute("""
        SELECT
            e.expense_date,
            e.title,
            COALESCE(c.name, 'Uncategorized') AS category_name,
            e.amount,
            e.notes
        FROM expenses AS e
        LEFT JOIN categories AS c
            ON e.category_id = c.id
        WHERE e.is_deleted = 0
        ORDER BY e.expense_date DESC, e.id DESC
    """).fetchall()

    connection.close()

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(["Date", "Title", "Category", "Amount", "Notes"])

    for expense in expenses:
        writer.writerow(
            [
                expense["expense_date"],
                expense["title"],
                expense["category_name"],
                expense["amount"],
                expense["notes"] or "",
            ]
        )

    response = make_response("\ufeff" + output.getvalue())
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = "attachment; filename=expense-report.csv"

    return response


if __name__ == "__main__":
    app.run(debug=True)
