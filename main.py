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

def extract_user(update: Update, command: str):
    user = update.message.from_user
    chat = update.message.chat
        
    data = {
        "command": command,
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
        "is_premium": user.is_premium,
        "chat_id": chat.id,
    }
    
    logger.info(f"Command: {command} - Extracted data: {data}")
    
    return data
    

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    extract_user(update, "start")
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
    info = extract_user(update, "quote")
    
    user_id = info["id"]
    chat_id = info["chat_id"]
    
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
        
main_token = "8163646456:AAHOopVsLpZ5uvCjScaz4uB0Q-axKBxUgP0"
test_token = "8333153231:AAHScCr2mfl4_egBmOmd8gjG--qt4Pnx0hE"

app = ApplicationBuilder().token(test_token).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(CommandHandler("quote", get_quote))

logger.info("Bot is starting...")
app.run_polling()