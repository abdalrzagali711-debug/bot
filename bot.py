import os
from flask import Flask, request
import requests

TOKEN = os.getenv("BOT_TOKEN")
URL = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is Running 🔥"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        requests.get(f"{URL}/sendMessage", params={
            "chat_id": chat_id,
            "text": f"تم الاستلام: {text}"
        })

    return {"ok": True}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))