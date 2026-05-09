import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from groq import Groq

# Loglarni sozlash
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# API Kalitlar (Bularni Render env-ga qo'shish tavsiya etiladi, lekin hozircha kodga qo'yamiz)
GROQ_API_KEY = "Gsk_LGzLksX775XtwDqDaP5mWGdyb3FYLoIwT5castH0kxmBatTQTy6x"
TELEGRAM_TOKEN = "8625557628:AAGcs0oVZS3SBpCdvdVq0SZC1igHWGpWQY" # Skrinshotdagi tokeningiz

# Groq mijozini ishga tushirish
client = Groq(api_key=GROQ_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Men Groq (Llama 3) bilan ishlovchi aqlli botman. Savolingizni bering!")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    try:
        # Groq-ga so'rov yuborish
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": user_message}],
            temperature=0.7,
            max_tokens=1024,
        )
        
        response = completion.choices[0].message.content
        await update.message.reply_text(response)
        
    except Exception as e:
        logging.error(f"Xatolik yuz berdi: {e}")
        await update.message.reply_text("Kechirasiz, javob berishda xatolik bo'ldi. Birozdan so'ng urinib ko'ring.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    # Handlerlarni qo'shish
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat))
    
    # Render uchun Polling rejimida ishga tushirish
    # Eslatma: Render "Web Service" bo'lsa, u port kutadi. 
    # Agar botingiz o'chib qolsa, buni "Background Worker" qilish kerak.
    application.run_polling()
   
    
