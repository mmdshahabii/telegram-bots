import logging
import requests
from config import TOKEN
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

from config import TOKEN, WEATHER_API_KEY

async def start_command(update : Update , context : ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"سلام {user_name}! ☁️\n"
        f"اسم شهر رو به انگلیسی بنویس تا وضعیت هوا رو بگم.\n"
        f"مثال: Tehran"
    )

async def get_weather(update : Update , context : ContextTypes.DEFAULT_TYPE):
    city=update.message.text
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=fa"

    try:
        response = requests.get(url)
        data = response.json()

        if data["cod"] == 200:
            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]
            description = data["weather"][0]["description"]
            wind_speed = data["wind"]["speed"]
            city_name = data["name"]
            country = data["sys"]["country"]


            message = (
                f"🌍 **آب و هوای {city_name}, {country}**\n\n"
                f"🌡 دما: **{temp}°C**\n"
                f"🤔 حس میشه: **{feels_like}°C**\n"
                f"💧 رطوبت: **{humidity}%**\n"
                f"💨 باد: **{wind_speed} m/s**\n"
                f"📝 وضعیت: **{description}**"
            )

            await update.message.reply_text(message , parse_mode="Markdown")

        else:
            await update.message.reply_text("❌ شهر پیدا نشد! اسم رو چک کن (انگلیسی بنویس).")

    except Exception as e:
        await update.message.reply_text("⚠️ مشکلی پیش اومد. دوباره تلاش کن.")
        print(f"Error: {e}")

def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_weather))
    
    print("✅ ربات هواشناسی روشن شد...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()