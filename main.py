from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import logging
import asyncio
import csv
import os

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger()

APP_MODE = "production"  # production | development
APP_DATA = {
    "production": {
        "token": "8163646456:AAHOopVsLpZ5uvCjScaz4uB0Q-axKBxUgP0",
        "file_path": "/data/data.csv"
    },
    "development": {
        "token": "8333153231:AAHScCr2mfl4_egBmOmd8gjG--qt4Pnx0hE",
        "file_path": "./data/data.csv"
    }
}

def save_user_to_csv(data: dict, filename=APP_DATA[APP_MODE]["file_path"]):
    file_exists = os.path.isfile(filename)

    with open(filename, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())

        if not file_exists:
            writer.writeheader()

        writer.writerow(data)

def extract_quote():
    url = "https://time.ir"

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    quote_container = soup.find("div", class_="ExpandableText_text__R_Pv6")
    if not quote_container:
        quote_container = soup.find("div", class_="ExpandableText_text__R_Pv6 ExpandableText_clamped__m5UVT")

    quote_text = quote_container.get_text(strip=True) if quote_container else "Quote not found."

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
        "id": user.id if user.id else 0,
        "first_name": user.first_name if user.first_name else "",
        "last_name": user.last_name if user.last_name else "",
        "username": user.username if user.username else "",
        "is_premium": user.is_premium if user.is_premium is True else 0,
        "chat_id": chat.id if chat.id else 0,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }
    
    logger.info(f"Command: {command} - Extracted data: {data}")

    save_user_to_csv(data)

    return data

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
        
app = ApplicationBuilder().token(APP_DATA[APP_MODE]["token"]).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(CommandHandler("quote", get_quote))

logger.info("Bot is starting...")
logger.info(f"Running in {APP_MODE} mode.")
app.run_polling()