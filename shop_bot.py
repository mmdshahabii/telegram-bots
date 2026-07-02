import logging
from config import TOKEN
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

PRODUCTS = {
    "python book":{
        "name" : "کتاب آموزش پایتون 📘",
        "price" : "220 هزار تومان",
        "description" : "کتاب کامل پایتون از مبتدی تا پیشرفته",
        "file_path" : "e:/GitHub/telegram-bots/files/python_book.pdf"
    },
    "robot_book": {
        "name": "کتاب ساخت ربات تلگرام 🤖",
        "price": "150 هزار تومان",
        "description": "آموزش ساخت ربات با پایتون + ۱۰ پروژه",
        "file_path" : "e:/GitHub/telegram-bots/files/robot_book.pdf"
    },
    "web_course": {
        "name": "دوره طراحی وب 💻",
        "price": "300 هزار تومان",
        "description": "دوره ۱۰ ساعته HTML, CSS, JavaScript",
        "file_path" : None
    }

}

CARD_NUMBER = "6037-9982-5637-3728"
CARD_HOLDER = "محمد شهابی"

async def start_command (update:Update , context:ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name

    keyboard=[]

    for product_id , product in PRODUCTS.items():
        keyboard.append([
            InlineKeyboardButton(f"{product["name"]} - {product["price"]}",callback_data=f"buy_{product_id}")
        ])
    
    keyboard.append([InlineKeyboardButton("پشتیبانی👤" , callback_data="support")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"سلام {user_name}! به فروشگاه ما خوش اومدی. 🛍\n\n"
        f"برای خرید روی محصول کلیک کن:",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_choice = query.data

    if user_choice == "support":
        await query.edit_message_text(
            "👤 برای پشتیبانی به [این آیدی](https://t.me/mmdshahabii) پیام بدید.",
            parse_mode="Markdown"
        )
        return
    
    if user_choice.startswith("buy_"):
        product_id=user_choice[4:]
        product=PRODUCTS[product_id]
        context.user_data["selected_product"] = product_id

        payment_text = (
            f"🛒 **محصول:** {product['name']}\n"
            f"💰 **قیمت:** {product['price']}\n"
            f"📝 **توضیحات:** {product['description']}\n\n"
            f"💳 **شماره کارت:** `{CARD_NUMBER}`\n"
            f"👤 **به نام:** {CARD_HOLDER}\n\n"
            f"📸 لطفاً رسید پرداخت رو آپلود کن."
        )

        await query.edit_message_text(payment_text , parse_mode="Markdown")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    if "selected_product" not in context.user_data:
        await update.message.reply_text("❌ لطفاً اول یه محصول انتخاب کن. /start رو بزن.")
        return
    
    product_id=context.user_data["selected_product"]
    product=PRODUCTS[product_id]

    await update.message.reply_text(
        f"✅ {user_name} جان، رسید دریافت شد!\n"
        f"📦 در حال ارسال {product['name']}..."
    )
    
    file_path=product.get("file_path")
    if file_path:
        try:
            with open(file_path , "rb") as file:
                await update.message.reply_document(
                    document=file ,
                    filename=f"{product['name']}.pdf" , 
                    caption=f"📦 {product['name']}\n\n🎉 ممنون از خریدت!"
                )
        except FileNotFoundError:
            await update.message.reply_text(
                "⚠️ فایل محصول موقتاً در دسترس نیست. با پشتیبانی تماس بگیر."
            )
    else:
        await update.message.reply_text(
        "📦 این محصول فایل دانلودی نداره. اطلاعات از طریق پیام ارسال می‌شه."
        )
    
    del context.user_data["selected_product"]

def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print("✅ ربات فروشگاهی روشن شد...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()