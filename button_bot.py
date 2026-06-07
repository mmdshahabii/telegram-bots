import logging
from config import TOKEN
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    
    keyboard = [
        [InlineKeyboardButton("خوب 😊", callback_data="good"),
         InlineKeyboardButton("متوسط 😐", callback_data="medium")],
        [InlineKeyboardButton("بد 😞", callback_data="bad")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"سلام {user_name}! حالت امروز چطوره؟",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_choice = query.data
    
    if user_choice == "good":
        response_text = "😍 عالیه! خوشحالم که حالت خوبه. روزت پر از انرژی!"
    elif user_choice == "medium":
        response_text = "🙂 روزهای معمولی هم قشنگن. امیدوارم بهتر بشه!"
    elif user_choice == "bad":
        response_text = "😔 متاسفم. یادت باشه روزای سخت می‌گذرن. فردا یه روز جدیده!"
    else:
        response_text = "متوجه نشدم چی زدی!"
    
    await query.edit_message_text(text=f"نظرت ثبت شد! {response_text}")

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    print("✅ ربات دکمه‌ای روشن شد...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()