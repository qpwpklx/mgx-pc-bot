import os
import time
import logging
from bot import main

# Настройка расширенного логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def check_environment():
    """Проверка переменных окружения"""
    logger.info("🔍 Проверка окружения...")
    
    bot_token = os.getenv("BOT_TOKEN")
    admin_ids = os.getenv("ADMIN_IDS", "[1271604471]")
    
    logger.info(f"BOT_TOKEN установлен: {'Да' if bot_token else 'Нет'}")
    logger.info(f"ADMIN_IDS: {admin_ids}")
    
    if not bot_token:
        logger.error("❌ BOT_TOKEN не найден в переменных окружения!")
        logger.info("💡 Убедитесь, что в Render добавлена переменная BOT_TOKEN")
        return False
    
    return True

if __name__ == '__main__':
    logger.info("🚀 Запуск MGX-PC бота...")
    
    # Проверяем окружение
    if not check_environment():
        exit(1)
    
    # Запускаем бота с перезапуском при ошибках
    max_retries = 5
    retry_delay = 10
    
    for attempt in range(max_retries):
        try:
            logger.info(f"🔄 Попытка запуска {attempt + 1}/{max_retries}")
            main()
        except Exception as e:
            logger.error(f"❌ Ошибка при запуске: {e}")
            logger.info(f"⏳ Перезапуск через {retry_delay} секунд...")
            time.sleep(retry_delay)
        else:
            break
    else:
        logger.error(f"❌ Не удалось запустить бота после {max_retries} попыток")