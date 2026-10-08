from flask import Flask, jsonify, request
from flask_cors import CORS
import asyncio
from database import init_db, get_all_users, get_stats, get_top_users, deactivate_user
from config import API_SECRET

app = Flask(__name__)
CORS(app)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

def run(coro):
    return loop.run_until_complete(coro)

def check_auth():
    return request.headers.get("X-API-Key") == API_SECRET

@app.before_request
def _init():
    if not hasattr(app, "_db_ready"):
        run(init_db())
        app._db_ready = True

@app.route("/api/stats")
def api_stats():
    if not check_auth():
        return jsonify({"error": "unauthorized"}), 401
    return jsonify(run(get_stats()))

@app.route("/api/users")
def api_users():
    if not check_auth():
        return jsonify({"error": "unauthorized"}), 401
    return jsonify(run(get_all_users()))

@app.route("/api/top")
def api_top():
    if not check_auth():
        return jsonify({"error": "unauthorized"}), 401
    return jsonify(run(get_top_users(10)))

@app.route("/api/ban/<int:user_id>", methods=["POST"])
def api_ban(user_id):
    if not check_auth():
        return jsonify({"error": "unauthorized"}), 401
    run(deactivate_user(user_id))
    return jsonify({"ok": True})

@app.route("/")
def root():
    return {"status": "bot api running"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)