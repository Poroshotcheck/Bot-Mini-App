import os
import logging
from dotenv import load_dotenv
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, MenuButtonWebApp
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from database import init_db, save_user, get_user_phone

# Загружаем переменные окружения
load_dotenv()

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем токен и URL из переменных окружения
TOKEN = os.getenv('TOKEN')
WEBAPP_URL = os.getenv('WEBAPP_URL')

# Проверяем наличие необходимых переменных окружения
if not TOKEN:
    raise ValueError("Не задан TOKEN. Проверьте файл .env")
if not WEBAPP_URL:
    raise ValueError("Не задан WEBAPP_URL. Проверьте файл .env")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /start"""
    user_id = update.effective_user.id
    
    # Проверяем, есть ли уже номер телефона
    existing_phone = get_user_phone(user_id)
    
    if existing_phone:
        # Если номер уже есть, сразу показываем кнопку Web App
        keyboard = [[
            InlineKeyboardButton(
                text="Открыть Support App",
                web_app=WebAppInfo(url=f"{WEBAPP_URL}?phone={existing_phone}&telegram_id={user_id}")
            )
        ]]
        markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Добро пожаловать в Support App!",
            reply_markup=markup
        )
    else:
        # Если номера нет, запрашиваем его
        keyboard = [[KeyboardButton(text="Предоставить номер телефона", request_contact=True)]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        
        await update.message.reply_text(
            "Для использования приложения, пожалуйста, предоставьте номер телефона:",
            reply_markup=reply_markup
        )

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка полученного контакта"""
    if update.message.contact:
        user_id = update.effective_user.id
        phone = update.message.contact.phone_number
        
        # Проверяем, есть ли уже номер в базе
        existing_phone = get_user_phone(user_id)
        if existing_phone:
            # Если номер уже есть, сообщаем об этом
            keyboard = [[
                InlineKeyboardButton(
                    text="Открыть Support App",
                    web_app=WebAppInfo(url=f"{WEBAPP_URL}?phone={existing_phone}&telegram_id={user_id}")
                )
            ]]
            markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "Вы уже поделились своим номером телефона. Используйте кнопку ниже для доступа к приложению:",
                reply_markup=markup
            )
        else:
            # Если номера нет, сохраняем его
            if save_user(user_id, phone):
                keyboard = [[
                    InlineKeyboardButton(
                        text="Открыть Support App",
                        web_app=WebAppInfo(url=f"{WEBAPP_URL}?phone={phone}&telegram_id={user_id}")
                    )
                ]]
                markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    "Спасибо! Теперь вы можете открыть приложение:",
                    reply_markup=markup
                )
            else:
                await update.message.reply_text(
                    "Произошла ошибка при сохранении данных. Попробуйте позже."
                )

async def setup_webapp_menu(application):
    """Настройка кнопки меню Web App"""
    try:
        await application.bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(
                text="Support App",
                web_app=WebAppInfo(url=f"{WEBAPP_URL}/check-auth")  # Специальный URL для проверки авторизации
            )
        )
        logger.info("Menu button set successfully")
    except Exception as e:
        logger.error(f"Error setting menu button: {e}")

async def main():
    """Запуск бота"""
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Настраиваем меню при запуске
    await setup_webapp_menu(app)
    
    # Добавляем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_webapp_data))
    
    await app.run_polling()

def main():
    """Запуск бота."""
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Добавляем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    
    app.run_polling()

if __name__ == '__main__':
    init_db()
    main()