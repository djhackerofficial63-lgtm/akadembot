import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from groq import Groq

# Loglarni yoqish (xatoni ko'rishimiz uchun)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- DIQQAT: SHU YERNI O'ZGARTIRING ---
GROQ_API_KEY = "Gsk_LGzLksX775XtwDqDaP5mWGdyb3FYLoIwT5castH0kxmBatTQTy6x"
# Yangi olgan tokeningizni pastdagi qo'shtirnoq ichiga qo'ying
TELEGRAM_TOKEN = "BU_YERGA_YANGI_TOKENNI_QO'YING" 
# --------------------------------------

client = Groq(api_key=GROQ_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Groq AI botingiz tayyor. Savol bering!")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": update.message.text}],
        )
        await update.message.reply_text(completion.choices[0].message.content)
    except Exception as e:
        logging.error(f"Xato: {e}")

if __name__ == '__main__':
    # Polling rejimi Render'da barqaror ishlaydi
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat))
    app.run_polling()
