from flask import Flask
import threading
import os
import time

app = Flask(__name__)

def run_bot():
    time.sleep(2)
    try:
        from bot import main
        print("🚀 Запуск бота в отдельном потоке...")
        main()
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")

@app.route("/")
def home():
    return "✅ MGX-PC Bot is running!"

@app.route("/health")
def health():
    return "OK"

if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
