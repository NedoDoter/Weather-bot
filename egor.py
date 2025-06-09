import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен бота (ЗАМЕНИТЕ НА СВОЙ)
TOKEN = "8095523929:AAFWM9OSrtfDMnJai2_1xfI3lIz4wmCwUIY"

# Клавиатура с городами
CITY_KEYBOARD = [
    ["Москва", "Санкт-Петербург"],
    ["Новосибирск", "Екатеринбург"],
    ["Казань", "Сочи"],
]
reply_markup = ReplyKeyboardMarkup(CITY_KEYBOARD, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет {user.mention_html()}! 🌤️ Я бот погоды. Напиши название города или выбери из списка:",
        reply_markup=reply_markup,
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    await update.message.reply_text(
        "Просто напиши мне название города (например, «Москва» или «London»), "
        "и я покажу текущую погоду.\n\n"
        "Или выбери город из клавиатуры ниже!",
        reply_markup=reply_markup,
    )

async def get_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение погоды с wttr.in"""
    city = update.message.text.strip()
    try:
        url = f"https://wttr.in/{city}?format=%C+%t+%h+%w+%P&lang=ru"
        response = requests.get(url, headers={"User-Agent": "curl/7.68.0"})
        
        if "Unknown location" in response.text:
            await update.message.reply_text("🚫 Город не найден. Попробуй другой!")
            return
        
        weather_data = response.text.split()
        
        # Проверка на корректность данных
        if len(weather_data) < 5:
            await update.message.reply_text("⚠️ Не удалось получить полные данные о погоде")
            return
            
        condition = weather_data[0]
        temp = weather_data[1]
        humidity = weather_data[2]
        wind = weather_data[3]
        pressure = weather_data[4]

        await update.message.reply_text(
            f"🌍 Погода в {city}:\n\n"
            f"🌡️ Температура: {temp}\n"
            f"☁️ Состояние: {condition}\n"
            f"💧 Влажность: {humidity}\n"
            f"💨 Ветер: {wind}\n"
            f"📊 Давление: {pressure}",
            reply_markup=reply_markup,
        )
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await update.message.reply_text("⚠️ Ошибка при запросе погоды. Попробуй позже.")

# ... (остальной код бота остаётся без изменений)

def main():
    """Запуск бота"""
    app = Application.builder().token(TOKEN).build()

    # Обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    
    # Обработчик текстовых сообщений
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_weather))

    # Запуск бота
    app.run_polling()

if __name__ == "__main__":
    main()