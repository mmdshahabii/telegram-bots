import logging
import json
import os
from config import TOKEN
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

ASK_NUMBER, ASK_NAME, ASK_AGE, ASK_PROBLEM = range(4)

DATA_FILE = "users.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load_data()
    if not users:
        await update.message.reply_text("هنوز هیچ کاربری ثبت نام نکرده ❌")
        return
    
    text = "📋 لیست کاربران ثبت‌نام شده:\n\n"
    for i, user in enumerate(users, 1):
        text += f"{i}. 👤 {user['name']} | 📱 {user['number']} | 🎂 {user['age']} سال\n"
        text += f"   📝 مشکل: {user['problem']}\n\n"
    
    await update.message.reply_text(text)

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
    return ASK_PROBLEM

async def get_problem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    problem = update.message.text

    new_user = {
        "name": context.user_data["name"],
        "age": context.user_data["age"],
        "number": context.user_data["number"],
        "problem": problem
    }

    users = load_data()
    users.append(new_user)
    save_data(users)

    await update.message.reply_text(
        f"✅ ثبت‌نام با موفقیت انجام شد!\n\n"
        f"👤 نام: {new_user['name']}\n"
        f"🎂 سن: {new_user['age']}\n"
        f"📱 شماره: {new_user['number']}\n"
        f"📝 مشکل: {problem}\n\n"
        f"به زودی باهات تماس می‌گیریم. 🙏"
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
            ASK_PROBLEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_problem)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("list", list_users))

    print("✅ ربات با قابلیت ذخیره‌سازی روشن شد...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()