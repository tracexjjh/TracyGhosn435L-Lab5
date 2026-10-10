import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATABASE = "database.db"


# ---------------- DATABASE ----------------

def connect_to_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


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


def row_to_dict(row):
    if row is None:
        return None
    return dict(row)


def get_users():
    conn = connect_to_db()
    try:
        rows = conn.execute(
            "SELECT * FROM users ORDER BY user_id"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


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


# ---------------- REST API ----------------

@app.route("/api/users", methods=["GET"])
def api_get_users():
    return jsonify(get_users()), 200


@app.route("/api/users/<int:user_id>", methods=["GET"])
def api_get_user(user_id):
    user = get_user_by_id(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user), 200


@app.route("/api/users/add", methods=["POST"])
def api_add_user():
    user = request.get_json(silent=True)

    required = ["name", "email", "phone", "address", "country"]
    if not isinstance(user, dict):
        return jsonify({"error": "A JSON object is required"}), 400

    if any(not isinstance(user.get(key), str) or not user[key].strip()
           for key in required):
        return jsonify({"error": "All user fields are required"}), 400

    created = insert_user(user)
    return jsonify(created), 201


@app.route("/api/users/update", methods=["PUT"])
def api_update_user():
    user = request.get_json(silent=True)

    required = [
        "user_id", "name", "email", "phone", "address", "country"
    ]
    if not isinstance(user, dict):
        return jsonify({"error": "A JSON object is required"}), 400

    if any(key not in user for key in required):
        return jsonify({"error": "All user fields, including user_id, are required"}), 400

    try:
        user["user_id"] = int(user["user_id"])
    except (TypeError, ValueError):
        return jsonify({"error": "user_id must be an integer"}), 400

    if any(not isinstance(user.get(key), str) or not user[key].strip()
           for key in required if key != "user_id"):
        return jsonify({"error": "All user fields must be non-empty strings"}), 400

    updated = update_user(user)
    if updated is None:
        return jsonify({"error": "User not found"}), 404

    return jsonify(updated), 200


@app.route("/api/users/delete/<int:user_id>", methods=["DELETE"])
def api_delete_user(user_id):
    result = delete_user(user_id)
    if result is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify(result), 200


if __name__ == "__main__":
    create_db_table()
    app.run(debug=True)