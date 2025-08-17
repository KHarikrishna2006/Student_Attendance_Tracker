import sqlite3

con = sqlite3.connect("attendance.db")
cur = con.cursor()

# Drop old students table (with roll_no)
cur.execute("DROP TABLE IF EXISTS students")

# Recreate with only 'id' and 'name'
cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
""")

# Drop & recreate teachers table
cur.execute("DROP TABLE IF EXISTS teachers")
cur.execute("""
    CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    )
""")

# Insert default teacher
cur.execute("INSERT INTO teachers (username, password) VALUES (?, ?)", ("hari", "hari123"))

con.commit()
con.close()
print("Database reset successfully with only student names!")
