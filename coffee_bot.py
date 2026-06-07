import logging
from config import TOKEN
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name

    keyboard = [
        [InlineKeyboardButton("اسپرسو ☕", callback_data="espresso"),
         InlineKeyboardButton("لاته 🥛", callback_data="latte"),
         InlineKeyboardButton("ماچا 🍵", callback_data="macha")],
        [InlineKeyboardButton("آب انبه 🥭", callback_data="mango"),
         InlineKeyboardButton("آب پرتقال 🍊", callback_data="orange")],
        [InlineKeyboardButton("بستنی 🍦", callback_data="ice_cream")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"سلام {user_name} خوش اومدید. چی میل دارید؟",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_choice = query.data
    
    if user_choice == "espresso":
        response_text = "سفارش اسپرسو ثبت شد! 5 دقیقه صبر کنید"
    elif user_choice == "latte":
        response_text = "سفارش لاته ثبت شد! 8 دقیقه صبر کنید"
    elif user_choice == "macha":
        response_text = "سفارش ماچا ثبت شد! 10 دقیقه صبر کنید"
    elif user_choice == "mango":
        response_text = "سفارش آب انبه ثبت شد! 7 دقیقه صبر کنید"
    elif user_choice == "orange":
        response_text = "سفارش آب پرتقال ثبت شد! 6 دقیقه صبر کنید"
    elif user_choice == "ice_cream":
        response_text = "سفارش بستنی ثبت شد! 1 دقیقه صبر کنید"
    else:
        response_text = "ناموجود"
    
    await query.edit_message_text(text=f"{response_text} - مرسی از شکیبایی شما.")

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    print("✅ ربات فعال است ✅")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()