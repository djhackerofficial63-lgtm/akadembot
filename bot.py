import os
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from groq import Groq

# Loglar
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# API Kalitlar
GROQ_API_KEY = "Gsk_LGzLksX775XtwDqDaP5mWGdyb3FYLoIwT5castH0kxmBatTQTy6x"
TELEGRAM_TOKEN = "SIZNING_YANGI_TOKENINGIZ" # BotFather bergan yangisini qo'ying

client = Groq(api_key=GROQ_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Bot muvaffaqiyatli yangilandi. Savol bering!")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": update.message.text}],
        )
        await update.message.reply_text(completion.choices[0].message.content)
    except Exception as e:
        logging.error(f"Xato: {e}")

async def main():
    # Application yaratish
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    # Handlerlarni qo'shish
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat))
    
    # Python 3.14+ uchun to'g'ri ishga tushirish
    async with app:
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        logging.info("Bot ishga tushdi...")
        # Bot to'xtab qolmasligi uchun cheksiz kutish
        while True:
            await asyncio.sleep(1)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
