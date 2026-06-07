import logging
import json
import os
from config import TOKEN
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler, CallbackQueryHandler

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

ASK_TASK_NAME, ASK_DEADLINE, ASK_PRIORITY = range(3)

DATA_FILE = "tasks.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name

    keyboard = [
        [InlineKeyboardButton("افزودن تسک جدید ➕", callback_data="add_task"),
         InlineKeyboardButton("مشاهده همه تسک ها 👁‍🗨", callback_data="show_tasks")],
        [InlineKeyboardButton("حذف همه تسک ها 🗑", callback_data="delete_all")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"سلام {user_name}! 👋\n"
        f"به مدیریت تسک خوش اومدی.\n"
        f"چه کاری برات انجام بدم؟",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_choice = query.data

    if user_choice == "add_task":
        await query.edit_message_text("📝 لطفا اسم تسک خود را وارد کنید:")
        return ASK_TASK_NAME
    elif user_choice == "show_tasks":
        tasks = load_data()
        if not tasks:
            await query.edit_message_text("❌ هیچ تسکی ثبت نشده!")
        else:
            text = "📋 لیست تسک‌ها:\n\n"
            for i, task in enumerate(tasks, 1):
                text += f"{i}. 📌 {task['name']}\n"
                text += f"   ⏰ {task['deadline']}\n"
                text += f"   🔥 اولویت: {task['priority']}\n\n"
            await query.edit_message_text(text)
    elif user_choice == "delete_all":
        save_data([])
        await query.edit_message_text("🗑 همه تسک‌ها حذف شدن!")

async def get_task_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["task_name"] = update.message.text
    await update.message.reply_text("⏰ deadline تسک رو وارد کن (مثلاً: جمعه ۱۰ صبح):")
    return ASK_DEADLINE

async def get_deadline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["deadline"] = update.message.text
    
    keyboard = [
        [InlineKeyboardButton("🟢 کم", callback_data="priority_low"),
         InlineKeyboardButton("🟡 متوسط", callback_data="priority_medium"),
         InlineKeyboardButton("🔴 زیاد", callback_data="priority_high")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🔥 اولویت تسک رو انتخاب کن:", reply_markup=reply_markup)
    return ASK_PRIORITY

async def get_priority(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    priority_data = query.data

    if priority_data == "priority_low":
        priority_text = "🟢 کم"
    elif priority_data == "priority_medium":
        priority_text = "🟡 متوسط"
    elif priority_data == "priority_high":
        priority_text = "🔴 زیاد"
    else:
        priority_text = "نامشخص"
    
    new_task = {
        "name": context.user_data["task_name"],
        "deadline": context.user_data["deadline"],
        "priority": priority_text
    }
    
    tasks = load_data()
    tasks.append(new_task)
    save_data(tasks)

    await query.edit_message_text(
        f"✅ تسک جدید با موفقیت ثبت شد!\n\n"
        f"📌 {new_task['name']}\n"
        f"⏰ {new_task['deadline']}\n"
        f"🔥 {new_task['priority']}"
    )

    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ عملیات لغو شد. برای شروع دوباره /start رو بزن.")
    context.user_data.clear()
    return ConversationHandler.END

def main():
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_callback, pattern="^add_task$")],
        states={
            ASK_TASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_task_name)],
            ASK_DEADLINE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_deadline)],
            ASK_PRIORITY: [CallbackQueryHandler(get_priority)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(button_callback, pattern="^(show_tasks|delete_all)$"))

    print("✅ ربات مدیریت تسک روشن شد...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()