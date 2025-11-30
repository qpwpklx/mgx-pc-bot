from flask import Flask
import threading
import os
import time
import subprocess
import sys

app = Flask(__name__)

def run_bot():
    """Запускает бота в отдельном процессе"""
    time.sleep(2)
    print("🚀 Запуск Telegram бота...")
    try:
        # Запускаем бота как отдельный процесс
        subprocess.run([sys.executable, "bot.py"])
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")

@app.route('/')
def home():
    return "✅ MGX-PC Bot is running!"

@app.route('/health')
def health():
    return "OK"

if __name__ == '__main__':
    print("🌐 Запуск Flask сервера...")
    
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    print("✅ Бот запущен в отдельном потоке")
    
    port = int(os.environ.get("PORT", 10000))
    print(f"📍 Порт: {port}")
    app.run(host='0.0.0.0', port=port, debug=False)