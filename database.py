import sqlite3

DATABASE = "database.db"


# ---------------- DATABASE CONNECTION ----------------

def connect_to_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- CREATE TABLE ----------------

def create_db_table():
    conn = connect_to_db()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                address TEXT NOT NULL,
                country TEXT NOT NULL
            )
        """)
        conn.commit()
        print("User table created successfully")
    finally:
        conn.close()


# ---------------- HELPER FUNCTION ----------------

def row_to_dict(row):
    if row is None:
        return None
    return dict(row)


# ---------------- GET ALL USERS ----------------

def get_users():
    conn = connect_to_db()
    try:
        rows = conn.execute(
            "SELECT * FROM users ORDER BY user_id"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


# ---------------- GET USER BY ID ----------------

def get_user_by_id(user_id):
    conn = connect_to_db()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        return row_to_dict(row)
    finally:
        conn.close()


# ---------------- INSERT USER ----------------

def insert_user(user):
    conn = connect_to_db()
    try:
        cursor = conn.execute("""
            INSERT INTO users (name, email, phone, address, country)
            VALUES (?, ?, ?, ?, ?)
        """, (
            user["name"],
            user["email"],
            user["phone"],
            user["address"],
            user["country"]
        ))
        conn.commit()
        user_id = cursor.lastrowid
    finally:
        conn.close()

    return get_user_by_id(user_id)


# ---------------- UPDATE USER ----------------

def update_user(user):
    conn = connect_to_db()
    try:
        cursor = conn.execute("""
            UPDATE users
            SET name = ?, email = ?, phone = ?,
                address = ?, country = ?
            WHERE user_id = ?
        """, (
            user["name"],
            user["email"],
            user["phone"],
            user["address"],
            user["country"],
            user["user_id"]
        ))
        conn.commit()
        updated = cursor.rowcount > 0
    finally:
        conn.close()

    if not updated:
        return None

    return get_user_by_id(user["user_id"])


# ---------------- DELETE USER ----------------

def delete_user(user_id):
    conn = connect_to_db()
    try:
        cursor = conn.execute(
            "DELETE FROM users WHERE user_id = ?",
            (user_id,)
        )
        conn.commit()
        deleted = cursor.rowcount > 0
    finally:
        conn.close()

    if not deleted:
        return None

    return {"status": "User deleted successfully"}