from flask import Flask, request, jsonify
from flask_cors import CORS

from database import (
    create_db_table,
    get_users,
    get_user_by_id,
    insert_user,
    update_user,
    delete_user
)

app = Flask(__name__)
CORS(app)


# ---------------- GET ALL USERS ----------------

@app.route("/api/users", methods=["GET"])
def api_get_users():
    return jsonify(get_users()), 200


# ---------------- GET USER BY ID ----------------

@app.route("/api/users/<int:user_id>", methods=["GET"])
def api_get_user(user_id):
    user = get_user_by_id(user_id)

    if user is None:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user), 200


# ---------------- ADD USER ----------------

@app.route("/api/users/add", methods=["POST"])
def api_add_user():
    user = request.get_json(silent=True)

    required = ["name", "email", "phone", "address", "country"]

    if not isinstance(user, dict):
        return jsonify({"error": "A JSON object is required"}), 400

    if any(
        not isinstance(user.get(key), str) or not user[key].strip()
        for key in required
    ):
        return jsonify({"error": "All user fields are required"}), 400

    created = insert_user(user)
    return jsonify(created), 201


# ---------------- UPDATE USER ----------------

@app.route("/api/users/update", methods=["PUT"])
def api_update_user():
    user = request.get_json(silent=True)

    required = [
        "user_id", "name", "email", "phone", "address", "country"
    ]

    if not isinstance(user, dict):
        return jsonify({"error": "A JSON object is required"}), 400

    if any(key not in user for key in required):
        return jsonify({
            "error": "All user fields, including user_id, are required"
        }), 400

    try:
        user["user_id"] = int(user["user_id"])
    except (TypeError, ValueError):
        return jsonify({"error": "user_id must be an integer"}), 400

    if any(
        not isinstance(user.get(key), str) or not user[key].strip()
        for key in required if key != "user_id"
    ):
        return jsonify({
            "error": "All user fields must be non-empty strings"
        }), 400

    updated = update_user(user)

    if updated is None:
        return jsonify({"error": "User not found"}), 404

    return jsonify(updated), 200


# ---------------- DELETE USER ----------------

@app.route("/api/users/delete/<int:user_id>", methods=["DELETE"])
def api_delete_user(user_id):
    result = delete_user(user_id)

    if result is None:
        return jsonify({"error": "User not found"}), 404

    return jsonify(result), 200


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":
    create_db_table()
    app.run(debug=True)