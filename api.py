# api.py — расширенная версия
import threading
import asyncio
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN, API_SECRET
from database import init_db, get_all_users, get_stats, get_top_users, deactivate_user
from handlers import register_all

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
db_ready = False

def run(coro):
    return loop.run_until_complete(coro)

def bot_thread():
    async def main():
        await init_db()
        bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        dp = Dispatcher()
        register_all(dp)
        await dp.start_polling(bot)
    asyncio.run(main())

threading.Thread(target=bot_thread, daemon=True).start()

def check_auth():
    return request.headers.get("X-API-Key") == API_SECRET

@app.before_request
def _ensure_db():
    global db_ready
    if not db_ready:
        run(init_db())
        db_ready = True

@app.route("/")
def root():
    return {"status": "ok", "bot": "running"}

@app.route("/api/stats")
def api_stats():
    if not check_auth(): return jsonify({"error":"unauthorized"}), 401
    return jsonify(run(get_stats()))

@app.route("/api/users")
def api_users():
    if not check_auth(): return jsonify({"error":"unauthorized"}), 401
    return jsonify(run(get_all_users()))

@app.route("/api/top")
def api_top():
    if not check_auth(): return jsonify({"error":"unauthorized"}), 401
    return jsonify(run(get_top_users(10)))

@app.route("/api/ban/<int:user_id>", methods=["POST"])
def api_ban(user_id):
    if not check_auth(): return jsonify({"error":"unauthorized"}), 401
    run(deactivate_user(user_id))
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
