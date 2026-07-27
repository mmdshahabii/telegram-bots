import logging
import requests
from config import TOKEN, DEEPSEEK_API_KEY
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

# تاریخچه مکالمه
user_conversations = {}

def chat_with_ai(user_id , user_message):
    if user_id not in user_conversations:
        user_conversations[user_id] = [
            {"role" : "system" , "content":"تو یه دستیار مفید و مهربون هستی. به فارسی جواب بده و پاسخ هات رو مختصر و مفید بگو."}
        ]

    user_conversations[user_id].append({"role" : "user" , "content" : user_message})

    headers = {
        "Authorization" : f"Bearer {DEEPSEEK_API_KEY}" ,
        "Context-Type" : "application/json"
    }

    data = {
        "model" : "deepseek-chat" ,
        "messages" : user_conversations[user_id] ,
        "max_tokens" : 500 ,
        "temperature" : 0.7
    }

    try:
        response = requests.post(DEEPSEEK_URL , headers=headers , json=data , timeout=30)
        result = response.json()

        if "choices" in result:
            bot_reply = result["choices"][0]["message"]["content"]
            user_conversations[user_id].append({"role":"assistant" , "content":bot_reply})
            return bot_reply
        else:
            print(f"DeepSeek Error: {result}")
            return "⚠️ خطا در دریافت پاسخ. دوباره تلاش کن."

    except Exception as e:
        print(f"Error: {e}")
        return "⚠️ مشکلی پیش اومد."

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    user_id = update.effective_user.id

    if user_id in user_conversations:
        del user_conversations[user_id]

    await update.message.reply_text(
        f"سلام {user_name}! 👋\n"
        f"من یه چت‌بات هوشمندم.\n\n"
        f"💬 هر سوالی داری ازم بپرس!\n"
        f"🔄 با /reset می‌تونی مکالمه رو از نو شروع کنی."
    )

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_conversations:
            del user_conversations[user_id]

    await update.message.reply_text("🔄 تاریخچه پاک شد! دوباره بپرس.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text

    await context.bot.send_chat_action(chat_id=update.effective_chat.id , action="typing")

    bot_reply = chat_with_ai(user_id , user_message)

    await update.message.reply_text(bot_reply)

def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("reset", reset_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ چت‌بات هوشمند رایگان روشن شد...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()