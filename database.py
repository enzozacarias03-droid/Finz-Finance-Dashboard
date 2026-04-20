import sqlite3



# Establishes and returns a connection to the SQLite database
# SQLite creates the file automatically if it doesn't exist yet
def get_connection():
    connection = sqlite3.connect("finance.db")
    return connection

# Creates the expenses table if it doesn't already exist
# Called once at app startup
def create_table():
    connection = get_connection()
    cursor = connection.cursor()

#Defining table structure with colums and data types
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

#Inserts a new expense row into the database
#Uses parameterized queries to prevent sql injection attacks
def add_expense(amount, category, description, date):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO expenses (amount, category, description, date)
        VALUES (?, ?, ?, ?)
    """, (amount, category, description, date))

    connection.commit()
    connection.close()

#Gets back all expense rows from the database
#Returns a list of tuples, each tuple is one expense row
def get_all_expenses():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()

    connection.close()
    return rows

#Deletes a single expense by its unique ID
#The comma comma in (expense_id,) turns it into a tuple as SQLite requires
def delete_expense(expense_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))

    connection.commit()
    connection.close

#Builds a human-readable spending summary grouped by category
#This text is then sent to AI so it can reason about real data
def get_expenses_summary():
    connection = get_connection()
    cursor = connection.cursor()

#Group expenses by category and calculate totals
    cursor.execute("""
        SELECT category, SUM(amount), COUNT(*)
        FROM expenses
        GROUP BY category
    """)

    rows = cursor.fetchall()
    connection.close()

#Format results as readable text for the AI prompt
    summary = "User's spending summary:\n"
    for row in rows:
        summary += f"- {row[0]}: €{row[1]:.2f} across {row[2]} transactions\n"

    return summary