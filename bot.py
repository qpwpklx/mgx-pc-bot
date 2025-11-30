import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Конфигурация
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [1271604471]  # ЗАМЕНИТЕ НА ВАШ ID

if not BOT_TOKEN:
    print("❌ ОШИБКА: BOT_TOKEN не установлен!")
    exit(1)

# Словарь для хранения данных пользователей
user_data_dict = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    
    welcome_text = f"""
✨ *Добро пожаловать в MGX-PC!* ✨

Привет, {user.first_name}! 🖥️

Мы создаем мощные компьютеры под любые задачи!

🎯 *Что мы предлагаем:*
• Индивидуальную сборку под ваш бюджет
• Профессиональный подбор компонентов  
• Гарантию качества и поддержку

Выберите действие: 👇
    """
    
    keyboard = [
        [InlineKeyboardButton("🛠️ Создать заявку", callback_data="create_order")],
        [InlineKeyboardButton("🌐 Наш сайт", callback_data="website")],
        [InlineKeyboardButton("📞 Тех. поддержка", callback_data="support")],
        [InlineKeyboardButton("💼 Наши работы", callback_data="portfolio")],
        [InlineKeyboardButton("ℹ️ О компании", callback_data="about")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.callback_query.edit_message_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "create_order":
        await create_order_start(query, context)
    elif query.data == "website":
        await show_website(query)
    elif query.data == "support":
        await show_support(query)
    elif query.data == "portfolio":
        await show_portfolio(query)
    elif query.data == "about":
        await show_about(query)
    elif query.data == "back_to_menu":
        await start(update, context)
    elif query.data.startswith("purpose_"):
        await handle_purpose(update, context)

async def create_order_start(query, context):
    """Начало создания заявки"""
    user_id = query.from_user.id
    user_data_dict[user_id] = {}
    
    text = """
🎯 *Создание заявки на сборку ПК*

📝 *Шаг 1 из 4*
Укажите ваш бюджет (в рублях):
    """
    
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    context.user_data['step'] = 'budget'

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    step = context.user_data.get('step', 'menu')
    
    if step == 'budget':
        await handle_budget(update, context)
    elif step == 'purpose':
        await handle_purpose_text(update, context)
    elif step == 'contact':
        await handle_contact(update, context)

async def handle_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ввода бюджета"""
    user_id = update.message.from_user.id
    budget_text = update.message.text
    
    # Проверяем, что введены цифры
    if not budget_text.isdigit():
        await update.message.reply_text("❌ Пожалуйста, введите бюджет цифрами:")
        return
    
    user_data_dict[user_id]['budget'] = int(budget_text)
    
    text = """
🎯 *Создание заявки на сборку ПК*

📝 *Шаг 2 из 4*
Для чего будет использоваться компьютер?
    """
    
    keyboard = [
        [InlineKeyboardButton("🎮 Игры", callback_data="purpose_gaming")],
        [InlineKeyboardButton("💼 Работа/офис", callback_data="purpose_work")],
        [InlineKeyboardButton("🎨 Дизайн/монтаж", callback_data="purpose_design")],
        [InlineKeyboardButton("🏠 Домашний ПК", callback_data="purpose_home")],
        [InlineKeyboardButton("🔙 Назад", callback_data="create_order")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    context.user_data['step'] = 'purpose'

async def handle_purpose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик выбора назначения через кнопки"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    purpose_map = {
        "purpose_gaming": "🎮 Игры",
        "purpose_work": "💼 Работа/офис", 
        "purpose_design": "🎨 Дизайн/монтаж",
        "purpose_home": "🏠 Домашний ПК"
    }
    
    user_data_dict[user_id]['purpose'] = purpose_map[query.data]
    
    text = """
🎯 *Создание заявки на сборку ПК*

📝 *Шаг 3 из 4*
Как с вами связаться?
Укажите телефон или Telegram:
    """
    
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="create_order")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    context.user_data['step'] = 'contact'

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ввода контактов"""
    user_id = update.message.from_user.id
    user_data_dict[user_id]['contact'] = update.message.text
    user_data_dict[user_id]['username'] = update.message.from_user.username
    user_data_dict[user_id]['full_name'] = f"{update.message.from_user.first_name} {update.message.from_user.last_name or ''}"
    
    # Отправка заявки администраторам
    await send_order_to_admins(context, user_id)
    
    # Подтверждение пользователю
    text = f"""
✅ *Заявка успешно создана!*

Спасибо, {update.message.from_user.first_name}!

📋 *Детали заявки:*
• Бюджет: {user_data_dict[user_id]['budget']:,} ₽
• Назначение: {user_data_dict[user_id]['purpose']}
• Контакты: {user_data_dict[user_id]['contact']}

Свяжемся с вами в ближайшее время! ⏰
    """
    
    keyboard = [[InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    context.user_data['step'] = 'menu'

async def send_order_to_admins(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Отправка заявки администраторам"""
    order_data = user_data_dict[user_id]
    
    order_text = f"""
🚨 *НОВАЯ ЗАЯВКА НА СБОРКУ ПК*

👤 *Клиент:*
• Имя: {order_data['full_name']}
• Username: @{order_data['username'] or 'Не указан'}
• Контакты: {order_data['contact']}

💰 *Бюджет:* {order_data['budget']:,} ₽
🎯 *Назначение:* {order_data['purpose']}

⏰ *Время:* {datetime.now().strftime('%d.%m.%Y %H:%M')}
    """
    
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=order_text,
                parse_mode='Markdown'
            )
        except Exception as e:
            print(f"Ошибка отправки админу {admin_id}: {e}")

async def show_website(query):
    text = """
🌐 *Наш сайт*

Посетите наш сайт:
mgx-pc.ru

Там вы найдете:
• Готовые сборки
• Отзывы клиентов  
• Акции и предложения
    """
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def show_support(query):
    text = """
📞 *Тех. поддержка*

🕐 *Время работы:*
Пн-Пт: 9:00 - 21:00
Сб-Вс: 10:00 - 18:00

📱 *Контакты:*
• Телефон: +7 (XXX) XXX-XX-XX
• Telegram: @mgx_support
    """
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def show_portfolio(query):
    text = """
💼 *Наши работы*

Примеры сборок:

🎮 *Игровые ПК:*
- Intel i7 + RTX 4070
- AMD Ryzen 5 + RX 7700 XT

💼 *Рабочие станции:*
- Для монтажа видео
- Графические рабочие станции
    """
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def show_about(query):
    text = """
ℹ️ *О компании MGX-PC*

🌟 *Наша миссия:* 
Создавать компьютеры, которые идеально подходят именно вам!

🔧 *Опыт:* 5+ лет
✅ *Качество:* проверенные компоненты
⚡ *Скорость:* сборка за 1-3 дня
    """
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def handle_purpose_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстового ввода назначения"""
    user_id = update.message.from_user.id
    user_data_dict[user_id]['purpose'] = update.message.text
    
    text = """
📝 *Шаг 3 из 4*
Как с вами связаться?
Укажите телефон или Telegram:
    """
    await update.message.reply_text(text, parse_mode='Markdown')
    context.user_data['step'] = 'contact'

def main():
    """Основная функция"""
    print("🚀 Запуск MGX-PC бота...")
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запуск
    application.run_polling()

if __name__ == '__main__':
    main()