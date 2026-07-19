import logging
import json
import os
import requests
from config import TOKEN, WEATHER_API_KEY
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, ContextTypes, CallbackQueryHandler,
    MessageHandler, filters, ConversationHandler
)

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

TASK_FILE = "super_tasks.json"
ASK_TASK , ASK_DEADLINE , ASK_PRIORITY = range(3)

def load_tasks():
    if os.path.exists(TASK_FILE):
        with open(TASK_FILE , "r" , encoding="utf-8") as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open (TASK_FILE , "w" , encoding="utf-8") as f:
        json.dump(tasks , f , ensure_ascii=False , indent=4)


# ==================== بخش آب و هوا ====================
def get_weather_text(city = "Tehran"):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=fa"
    try:
        response = requests.get(url , timeout=10)
        data = response.json()
        if data["cod"]==200:
            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]
            description = data["weather"][0]["description"]
            wind = data["wind"]["speed"]
            city_name = data["name"]
            country = data["sys"]["country"]

            return(
                f"🌍 **آب و هوای {city_name},{country}**\n\n"
                f"🌡 دما: **{temp}°C**\n"
                f"🤔 حس می‌شه: **{feels_like}°C**\n"
                f"💧 رطوبت: **{humidity}٪**\n"
                f"💨 باد: **{wind} m/s**\n"
                f"📝 وضعیت: **{description}**"
            )
        return "❌ شهر پیدا نشد."
    except:
        return "⚠️ خطا در دریافت آب و هوا."


# ==================== بخش ارز دیجیتال ====================
def get_crypto_text():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids" : "bitcoin,ethereum,tether",
        "vs_currencies" : "usd",
        "include_24hr_change" : "true"
    }
    try:
        response = requests.get(url , params=params , timeout=10)
        data = response.json()

        crypto_list = {
            "bitcoin": "بیت‌کوین (BTC)",
            "ethereum": "اتریوم (ETH)",
            "tether": "تتر (USDT)"
        }

        text = "🪙 **قیمت ارزهای دیجیتال:**\n\n"
        for coin_id , coin_name in crypto_list.items():
            if coin_id in data:
                price = data[coin_id]["usd"]
                change = data[coin_id].get("usd_24h_change" , 0)
                emoji = "🟢" if change > 0 else "🔴" if change < 0 else "⚪"
                text += f"{coin_name}: **${price:,.2f}** {emoji} {change:.2f}%\n"
        return text
    except:
        return "❌ خطا در دریافت قیمت ارز دیجیتال."
    

# ==================== بخش ارز سنتی ====================
def get_currency_text():
    url = "https://api.exchangerate-api.com/v4/latest/USD"
    try:
        response = requests.get(url , timeout=10)
        data = response.json()
        rates = data["rates"]
        usd_irr = 180000

        text = "💵 **قیمت ارزهای سنتی:**\n\n"
        text += f"💰 دلار آمریکا: **{usd_irr:,} تومان**\n"
        text += f"💶 یورو: **{rates['EUR'] * usd_irr:,.0f} تومان**\n"
        text += f"💷 پوند: **{rates["GBP"] * usd_irr:,.0f} تومان**\n"
        return text
    except:
        return "❌ خطا در دریافت قیمت ارز."
    

# ==================== منوی اصلی ====================
async def main_menu(update: Update , context: ContextTypes.DEFAULT_TYPE , user_name ="" , edit=False):
    if not user_name:
        user_name = update.effective_user.first_name

    keyboard = [
        [InlineKeyboardButton("☁️ آب و هوا" , callback_data="weather") , InlineKeyboardButton("🪙 ارز دیجیتال" , callback_data="crypto_menu")],
        [InlineKeyboardButton("💵 ارز سنتی" , callback_data="currency_menu") , InlineKeyboardButton("📝 مدیریت تسک" , callback_data="task_menu")],
        [InlineKeyboardButton("📄 فایل آموزشی" , callback_data="file_menu") , InlineKeyboardButton("👤 پشتیبانی" , callback_data="support")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        f"سلام {user_name}! 👋\n"
        f"به ربات جامع ابزارهای روزمره خوش اومدی.\n\n"
        f"🛠 **چه کاری برات انجام بدم؟**"
    )

    if edit:
        query = update.callback_query
        await query.edit_message_text(text , reply_markup=reply_markup , parse_mode="Markdown")
    else:
        await update.message.reply_text(text , reply_markup=reply_markup , parse_mode="Markdown")

async def start_command(update: Update , context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await main_menu(update , context , user_name)


# ==================== مدیریت دکمه‌ها ====================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data

    if choice == "weather":
        text = get_weather_text()
        text += "\n\n💡 _برای شهر دیگه، اسمش رو تایپ کن._"
        keyboard = [[InlineKeyboardButton("🔙 بازگشت" , callback_data="main_menu")]]
        await query.edit_message_text(text , reply_markup=InlineKeyboardMarkup(keyboard) , parse_mode="Markdown")
    
    elif choice == "crypto_menu":
        text = get_crypto_text()
        keyboard = [[InlineKeyboardButton("🔄 بروزرسانی" , callback_data="crypto_menu") , InlineKeyboardButton("🔙 بازگشت" , callback_data="main_menu")]]
        await query.edit_message_text(text , reply_markup=InlineKeyboardMarkup(keyboard) , parse_mode="Markdown")
    
    elif choice == "currency_menu":
        text = get_currency_text()
        keyboard = [[InlineKeyboardButton("🔙 بازگشت" , callback_data="main_menu")]]
        await query.edit_message_text(text , reply_markup=InlineKeyboardMarkup(keyboard) , parse_mode="Markdown")
    
    elif choice == "task_menu":
        keyboard = [
            [InlineKeyboardButton("➕ افزودن تسک" , callback_data="add_task")],
            [InlineKeyboardButton("📋 مشاهده تسک‌ها" , callback_data="show_tasks")],
            [InlineKeyboardButton("🗑 حذف همه" , callback_data="delete_tasks")],
            [InlineKeyboardButton("🔙 بازگشت" , callback_data="main_menu")]
        ]
        await query.edit_message_text(
            "📝 **مدیریت تسک‌ها**\nچه کاری می‌خوای انجام بدی؟",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    elif choice == "show_tasks":
        tasks = load_tasks()
        if not tasks:
            text = "📝 هیچ تسکی ثبت نشده!"
        else:
            text = "📋 **تسک‌های تو:**\n\n"
            for i , task in enumerate(tasks , 1):
                text += f"{i}. 📌 {task["name"]}\n"
                text += f"   ⏰ {task["deadline"]} | 🔥 {task["priority"]}\n\n"
        keyboard = [[InlineKeyboardButton("🔙 بازگشت" , callback_data="task_menu")]]
        await query.edit_message_text(text , reply_markup=InlineKeyboardMarkup(keyboard) , parse_mode="Markdown")
    elif choice == "delete_tasks":
        save_tasks([])
        await query.answer("همه تسک‌ها حذف شدن! 🗑" , show_alert=True)
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="task_menu")]]
        await query.edit_message_text("🗑 همه تسک‌ها حذف شدن." , reply_markup=InlineKeyboardMarkup(keyboard))
    elif choice == "add_task":
        await query.edit_message_text("📝 اسم تسک رو وارد کن:")
        return ASK_TASK
    
    elif choice == "file_menu":
        text = "📄 **فایل آموزشی رایگان**\n\nروی دکمه زیر کلیک کن تا فایل رو دریافت کنی."
        keyboard = [
            [InlineKeyboardButton("📥 دریافت فایل PDF" , callback_data="send_file")],
            [InlineKeyboardButton("🔙 بازگشت" , callback_data="main_menu")]
        ]
        await query.edit_message_text(text , reply_markup=InlineKeyboardMarkup(keyboard) , parse_mode="Markdown")

    elif choice == "send_file":
        try:
            with open("files/python_book.pdf" , "rb") as file:
                await query.message.reply_document(
                    document=file,
                    filename="کتاب_آموزش_پایتون.pdf",
                    caption="📚 کتاب آموزش پایتون\n\n🎉 امیدوارم مفید باشه!"
                )
            await query.answer("فایل ارسال شد! 📥" , show_alert=True)
        except FileNotFoundError:
            await query.answer("فایل پیدا نشد! ⚠️" , show_alert=True)

    elif choice =="support":
        text = "👤 **پشتیبانی**\n\nبرای ارتباط با ادمین به آیدی زیر پیام بده:\n💬 [@mmdshahabii](https://t.me/mmdshahabii)"
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]]
        await query.edit_message_text(text , reply_markup=InlineKeyboardMarkup(keyboard) , parse_mode= "Markdown")

    elif choice == "main_menu":
        user_name = query.from_user.first_name
        await main_menu(update , context , user_name , edit=True)


# ==================== بخش تسک (ConversationHandler) ====================
async def get_task_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["task_name"] = update.message.text
    await update.message.reply_text("⏰ ددلاین تسک رو وارد کن (مثلاً: جمعه ۱۰ صبح):")
    return ASK_DEADLINE
async def get_deadline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["deadline"] = update.message.text
    keyboard = [
        [InlineKeyboardButton("🟢 کم", callback_data="priority_low"),
     InlineKeyboardButton("🟡 متوسط", callback_data="priority_medium"),
     InlineKeyboardButton("🔴 زیاد", callback_data="priority_high")]
    ]
    await update.message.reply_text("🔥 اولویت تسک رو انتخاب کن:" , reply_markup=InlineKeyboardMarkup(keyboard))
    return ASK_PRIORITY
async def get_priority(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    priority_data = query.data

    if priority_data == "priority_low":
        priority_text = "🟢 کم"
    elif priority_data == "priority_medium":
        priority_text = "🟡 متوسط"
    else:
        priority_text = "🔴 زیاد"

    new_task = {
        "name" : context.user_data["task_name"] ,
        "deadline" : context.user_data["deadline"] ,
        "priority" : priority_text
    }

    tasks = load_tasks()
    tasks.append(new_task)
    save_tasks(tasks)

    await query.edit_message_text(
        f"✅ تسک جدید اضافه شد!\n\n"
        f"📌 {new_task['name']}\n"
        f"⏰ {new_task['deadline']}\n"
        f"🔥 {new_task['priority']}"
    )

    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="main_menu")]]
    await update.message.reply_text(
        "❌ عملیات لغو شد.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ConversationHandler.END


# ==================== دریافت پیام متنی (آب و هوای شهر دلخواه) ====================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text
    text = get_weather_text(city)
    await update.message.reply_text(text , parse_mode="Markdown")


# ==================== تابع اصلی ====================
def main():
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern="^add_task$")],
        states={
            ASK_TASK: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_task_name)],
            ASK_DEADLINE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_deadline)],
            ASK_PRIORITY: [CallbackQueryHandler(get_priority)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        conversation_timeout=60,
    )

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(button_handler, pattern="^(weather|crypto_menu|currency_menu|task_menu|show_tasks|delete_tasks|file_menu|send_file|support|main_menu)$"))
    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("✅ ربات جامع روشن شد...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()