import sqlite3


def get_connection():
    connection = sqlite3.connect("finance.db")
    return connection


def create_table():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
      CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        description TEXT,
        date TEXT NOT NULL                           
)
    """)
  
    connection.commit()
    connection.close()


def add_expense(amount, category, description, date):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO expenses (amount, category, description, date)
        VALUES (?, ?, ?, ?)
    """, (amount, category, description, date))

    connection.commit()
    connection.close()


def get_all_expenses():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()

    connection.close()
    return rows


def delete_expense(expense_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))

    connection.commit()
    connection.close

def get_expenses_summary():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT category, SUM(amount), COUNT(*)
        FROM expenses
        GROUP BY category
    """)

    rows = cursor.fetchall()
    connection.close()

    summary = "User's spending summary:\n"
    for row in rows:
        summary += f"- {row[0]}: €{row[1]:.2f} across {row[2]} transactions\n"

    return summary