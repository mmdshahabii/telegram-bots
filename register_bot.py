import logging
from config import TOKEN
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

ASK_NUMBER, ASK_NAME, ASK_AGE, ASK_SUPPORT = range(4)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"سلام {user_name} جان! برای ثبت نام لطفا نام و نام خانوادگی خود را وارد کنید:"
    )
    return ASK_NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_full_name = update.message.text
    context.user_data["name"] = user_full_name
    await update.message.reply_text(
        f"اسمت ثبت شد: {user_full_name}\nحالا لطفا سنت را وارد کن:"
    )
    return ASK_AGE

async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_age = update.message.text
    context.user_data["age"] = user_age
    await update.message.reply_text(
        f"سنت ثبت شد: {user_age}\nحالا لطفا شماره تماس خود را وارد کنید:"
    )
    return ASK_NUMBER

async def get_num(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_number = update.message.text
    context.user_data["number"] = user_number
    await update.message.reply_text(
        f"شماره شما ثبت شد: {user_number}\nچگونه میتوانم کمکتون کنم؟"
    )
    return ASK_SUPPORT

async def get_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_support = update.message.text
    context.user_data["support"] = user_support

    name = context.user_data["name"]
    age = context.user_data["age"]
    number = context.user_data["number"]
    support = context.user_data["support"]

    await update.message.reply_text(
        f"✅ ثبت‌نام با موفقیت انجام شد!\n\n"
        f"👤 نام: {name}\n"
        f"🎂 سن: {age}\n"
        f"📱 شماره تماس: {number}\n"
        f"📃 سوال: {support}\n\n"
        f"به زودی برای پشتیبانی با شما تماس میگیریم.\n"
        f"ازت ممنونم! 🙏"
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ عملیات لغو شد.")
    return ConversationHandler.END

def main():
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_command)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            ASK_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
            ASK_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_num)],
            ASK_SUPPORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_support)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    
    print("✅ ربات ثبت‌نام روشن شد...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()