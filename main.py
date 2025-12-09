import logging
import asyncio

from bs4 import BeautifulSoup
import requests

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

def extract_quote():
    url = "https://time.ir"

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # --- Extract quote text ---
    quote_container = soup.find("div", class_="ExpandableText_text__R_Pv6")
    if not quote_container:
        # fallback: sometimes both classes may be needed
        quote_container = soup.find("div", class_="ExpandableText_text__R_Pv6 ExpandableText_clamped__m5UVT")

    quote_text = quote_container.get_text(strip=True) if quote_container else "Quote not found."

    # --- Extract author name + link ---
    author_div = soup.find("div", class_="BrainyQuoteAuthor_root__6iSkt")

    if author_div:
        a_tag = author_div.find("a")
        author_name = a_tag.get_text(strip=True) if a_tag else "Author not found."
        author_href = a_tag["href"] if a_tag and a_tag.has_attr("href") else "Link not found."
    else:
        author_name = "Author not found."
        author_href = "Link not found."

    return {
        "quote": quote_text,
        "author": author_name,
        "reference": author_href
    }

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"Received /start command from user {update.message.from_user.id}")
    
    messages = [
        "اگر احساس می‌کنید دنیا به اندازه کافی گهربار نیست، این ربات آماده است تا یک جرعه حکمت به روزتان اضافه کند. 🌟",
        "",
        "برای دریافت یک جمله گهربار، کافیست دستور /quote را ارسال کنید تا فلسفه بخوانید یا عارف شوید!",
        "",
        "ساخته شده توسط: @GNU_Jupiter 🙃"
    ]
    
    message = "\n".join(messages)
    
    await update.message.reply_text(message)

async def get_quote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    chat_id = update.message.chat.id
    
    logger.info(f"Quote command received from user {user_id} with chat ID {chat_id}")
    
    quote = extract_quote()
        
    messages = [
        quote['quote'],
        "",
        quote['author']
    ]
    
    message = "\n".join(messages)
    await update.message.reply_text(message)
    
    await asyncio.sleep(0.5)
        
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat.id
    logger.info(f"Chat command received from user {update.message.from_user.id} with chat ID {chat_id}")
    
    messages = [f"💬 Chat ID: {chat_id}"]
    await update.message.reply_text("\n".join(messages), reply_to_message_id=update.message.message_id)

async def me(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    logger.info(f"User info requested by {user.id}")
    
    messages = [
        f"🆔 User ID: {user.id}",
        f"👤 First Name: {user.first_name}",
        f"👥 Last Name: {user.last_name or 'N/A'}",
        f"📛 Username: @{user.username or 'N/A'}",
        f"⭐️ Premium Status: {'Yes 🎉' if user.is_premium else 'No 😢'}",
    ]
    await update.message.reply_text("\n".join(messages), reply_to_message_id=update.message.message_id)

app = ApplicationBuilder().token("8163646456:AAHOopVsLpZ5uvCjScaz4uB0Q-axKBxUgP0").build()

app.add_handler(CommandHandler("start", start))

app.add_handler(CommandHandler("quote", get_quote))

app.add_handler(CommandHandler("chat", chat))
app.add_handler(CommandHandler("me", me))

logger.info("Bot is starting...")
app.run_polling()