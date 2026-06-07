import logging
from config import TOKEN
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name

    keyboard = [
        [InlineKeyboardButton("فایل آموزشی 📄", callback_data="get_file"),
         InlineKeyboardButton("پشتیبانی 👤", callback_data="support")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"سلام {user_name} جان! چطور می‌تونم کمکت کنم؟",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_choice = query.data

    if user_choice == "get_file":
        await query.edit_message_text("📄 فایل آموزشی ارسال شد!")
    elif user_choice == "support":
        await query.edit_message_text(
            "👤 برای پشتیبانی به [این آیدی](https://t.me/mmdshahabii) پیام بدید.",
            parse_mode="Markdown"
        )
    else:
        await query.edit_message_text("❌ خطا!")

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    print("✅ ربات فعال است ✅")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()