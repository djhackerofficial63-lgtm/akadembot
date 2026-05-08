import logging
import anthropic
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters,
)

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = "8625557628:AAGcsOoVZS3SBpCpdvdVq0SZC1igHWGpWQY"
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "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")
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
user_mode = {}

SYSTEM_PROMPTS = {
    "slayd": "Siz talabalar uchun professional prezentatsiya yaratib beradigan yordamchisiz. Foydalanuvchi mavzu beradi, siz esa har bir slayd uchun sarlavha va 4-5 ta asosiy nuqta bilan batafsil prezentatsiya tarkibini o'zbek tilida tayyorlaysiz.",
    "kurs_ishi": "Siz talabalar uchun kurs ishi yozib beradigan akademik yordamchisiz. Kirish, nazariy asoslar, tahlil, xulosa va adabiyotlar ro'yxati bilan to'liq kurs ishi yozasiz. O'zbek tilida, ilmiy uslubda.",
    "maqola": "Siz ilmiy maqolalar yozib beradigan yordamchisiz. Annotatsiya, kalit so'zlar, kirish, asosiy qism, xulosa va adabiyotlar bilan to'liq maqola yozasiz. O'zbek tilida.",
    "referat": "Siz talabalar uchun referat tayyorlab beradigan yordamchisiz. Kirish, asosiy qism (3-4 bo'lim), xulosa va adabiyotlar bilan to'liq referat yozasiz. O'zbek tilida.",
    "esse": "Siz esse yozib beradigan yordamchisiz. Erkin, ijodiy, asosli esse yozasiz. 500-800 so'z. O'zbek tilida.",
    "test": "Siz test savollari tuzib beradigan yordamchisiz. A,B,C,D variantli testlar tuzasiz, to'g'ri javobni oxirida ko'rsatasiz.",
    "tarjima": "Siz professional tarjimon yordamchisiz. Berilgan matnni so'ralgan tilga aniq tarjima qilasiz.",
    "umumiy": "Siz o'zbek tilida gaplashadigan, talabalarga yordam beradigan universal AI yordamchisiz.",
}

VAZIFA_NOMI = {
    "slayd": "📊 Slayd tayyorlash", "kurs_ishi": "📝 Kurs ishi",
    "maqola": "📄 Maqola", "referat": "📚 Referat",
    "esse": "✍️ Esse", "test": "🧪 Test",
    "tarjima": "🌐 Tarjima", "umumiy": "💬 Erkin suhbat",
}

VAZIFA_SAVOL = {
    "slayd": "📊 Qaysi mavzu bo'yicha prezentatsiya tayyorlay?",
    "kurs_ishi": "📝 Qaysi mavzu bo'yicha kurs ishi yozay?",
    "maqola": "📄 Qaysi mavzu bo'yicha maqola yozay?",
    "referat": "📚 Qaysi mavzu bo'yicha referat tayyorlay?",
    "esse": "✍️ Qaysi mavzu bo'yicha esse yozay?",
    "test": "🧪 Mavzu va nechta test kerakligini yozing.",
    "tarjima": "🌐 Matn va qaysi tilga tarjima kerakligini yozing.",
    "umumiy": "💬 Savolingizni yozing!",
}

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Slayd", callback_data="slayd"), InlineKeyboardButton("📝 Kurs ishi", callback_data="kurs_ishi")],
        [InlineKeyboardButton("📄 Maqola", callback_data="maqola"), InlineKeyboardButton("📚 Referat", callback_data="referat")],
        [InlineKeyboardButton("✍️ Esse", callback_data="esse"), InlineKeyboardButton("🧪 Test", callback_data="test")],
        [InlineKeyboardButton("🌐 Tarjima", callback_data="tarjima"), InlineKeyboardButton("💬 Erkin suhbat", callback_data="umumiy")],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"👋 Salom *{update.effective_user.first_name}*!\n\n🎓 Men *Akadem Yordamchi* — talabalarga mo'ljallangan AI yordamchiman!\n\nVazifani tanlang 👇",
        parse_mode="Markdown", reply_markup=main_menu()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "menu":
        user_mode.pop(query.from_user.id, None)
        await query.edit_message_text("🏠 Asosiy menyu 👇", reply_markup=main_menu())
        return
    user_mode[query.from_user.id] = query.data
    await query.edit_message_text(
        VAZIFA_SAVOL.get(query.data, "Mavzuni yozing:"),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Menyu", callback_data="menu")]])
    )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    mode = user_mode.get(user_id, "umumiy")
    thinking = await update.message.reply_text(f"⏳ {VAZIFA_NOMI.get(mode)} bajarilmoqda...")
    try:
        response = client.messages.create(
            model="claude-opus-4-5", max_tokens=4000,
            system=SYSTEM_PROMPTS.get(mode), messages=[{"role": "user", "content": update.message.text}]
        )
        await thinking.delete()
        text = response.content[0].text
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Yana", callback_data=mode), InlineKeyboardButton("🏠 Menyu", callback_data="menu")]])
        for i in range(0, len(text), 4000):
            chunk = text[i:i+4000]
            if i + 4000 >= len(text):
                await update.message.reply_text(chunk, reply_markup=kb)
            else:
                await update.message.reply_text(chunk)
    except Exception as e:
        logger.error(e)
        await thinking.edit_text("❌ Xatolik! /start bosing.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📌 /start — Botni ishga tushirish\n📌 /menu — Asosiy menyu", reply_markup=main_menu())

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_mode.pop(update.effective_user.id, None)
    await update.message.reply_text("🏠 Asosiy menyu 👇", reply_markup=main_menu())

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("menu", menu_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    logger.info("Bot ishga tushdi!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
