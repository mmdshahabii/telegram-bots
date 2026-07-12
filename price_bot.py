import logging
import requests
from config import TOKEN
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

def get_crypto_prices():
    """CoinGecko دریافت قیمت ارزهای دیجیتال از"""
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids" : "bitcoin,ethereum,tether,binancecoin,ripple",
        "vs_currencies" : "usd",
        "include_24hr_change" : "true"
    }

    try:
        response = requests.get(url , params=params , timeout=10)
        data = response.json()
        print(data)

        crypto_list = {
            "bitcoin": "بیت‌کوین (BTC)",
            "ethereum": "اتریوم (ETH)",
            "tether": "تتر (USDT)",
            "binancecoin": "بایننس کوین (BNB)",
            "ripple": "ریپل (XRP)"
        }

        text = "💸 **قیمت ارزهای دیجیتال (دلار):**\n\n"

        for coin_id , coin_name in crypto_list.items():
            if coin_id in data:
                price = data [coin_id]["usd"]
                change = data[coin_id].get("usd_24h_change", 0)
                
                if change>0:
                    emoji = "🟢"
                elif change<0:
                    emoji = "🔴"
                else:
                    emoji = "⚪"
                
                text += f"{coin_name}: **${price:,.2f}** {emoji} {change:.2f}%\n"
        
        return text

    except Exception as e:
        print(f"Error fetching crypto: {e}")
        return "❌ خطا در دریافت قیمت ارزهای دیجیتال."

def get_currency_prices():
    """دریافت قیمت ارزهای سنتی (دلار، یورو و...)"""
    url = "https://api.exchangerate-api.com/v4/latest/USD"

    try:
        response = requests.get(url , timeout=10)
        data = response.json()
        rates = data["rates"]

        usd_irr = get_usd_irr()

        text = "💵 **قیمت ارزهای سنتی:**\n\n"
        text += f"💰 دلار آمریکا: **{usd_irr:,} تومان**\n"
        text += f"💶 یورو: **{rates['EUR'] * usd_irr:,.0f} تومان**\n"
        text += f"💷 پوند انگلیس: **{rates['GBP'] * usd_irr:,.0f} تومان**\n"
        text += f"🇹🇷 لیر ترکیه: **{rates['TRY'] * usd_irr:,.0f} تومان**\n"

        return text
    
    except Exception as e:
        print(f"Error fetching currencies: {e}")
        return "❌ خطا در دریافت قیمت ارزها."

def get_usd_irr():
    """دریافت قیمت دلار از API داخلی"""
    url = "https://api.tgju.org/v1/market/indicator/summary/price_dollar_rl"

    try:
        response = requests.get(url , timeout=10)
        data = response.json()
        return data["response"]["indicators"]["p"]["p"]
    except:
        return 175000

def get_gold_prices():
    return "🥇 **قیمت طلا و سکه:**\n\n⚠️ در حال حاضر در دسترس نیست. لطفاً از منابع داخلی استعلام بگیرید."


async def start_command(update:Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name

    keyboard = [
        [InlineKeyboardButton("🪙 ارزهای دیجیتال" , callback_data="crypto")],
        [InlineKeyboardButton("💵 ارزهای سنتی" , callback_data="currency")],
        [InlineKeyboardButton("🥇 طلا و سکه" , callback_data="gold")],
        [InlineKeyboardButton("📊 همه قیمت‌ها" , callback_data="all")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"سلام {user_name}! 👋\n"
        f"به ربات قیمت‌ها خوش اومدی.\n\n"
        f"چه قیمتی رو می‌خوای ببینی؟",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_choice = query.data

    if user_choice=="crypto":
        text = get_crypto_prices()
    elif user_choice=="currency":
        text = get_currency_prices()
    elif user_choice=="gold":
        text = get_gold_prices()
    elif user_choice=="all":
        text = get_crypto_prices() + "\n" + get_currency_prices() + "\n" + get_gold_prices()
    else:
        text = "متوجه نشدم!"
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text , parse_mode="Markdown" , reply_markup=reply_markup)

async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("🪙 ارزهای دیجیتال" , callback_data="crypto")],
        [InlineKeyboardButton("💵 ارزهای سنتی" , callback_data="currency")],
        [InlineKeyboardButton("🥇 طلا و سکه" , callback_data="gold")],
        [InlineKeyboardButton("📊 همه قیمت‌ها" , callback_data="all")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"چه قیمتی رو می‌خوای ببینی؟",
        reply_markup=reply_markup
    )

def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(button_callback, pattern="^(crypto|currency|gold|all)$"))
    application.add_handler(CallbackQueryHandler(back_to_main, pattern="^back$"))
    
    print("✅ ربات قیمت‌ها روشن شد...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()