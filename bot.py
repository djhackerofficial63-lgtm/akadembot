import os
import json
import urllib.request
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "8625557628:AAGcsOoVZS3SBpCpdvdVq0SZC1igHWGpWQY"
API_KEY = "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"
PORT = int(os.environ.get("PORT", 8080))

user_mode = {}

PROMPTS = {
    "slayd": "Siz professional prezentatsiya yaratib beradigan yordamchisiz. O'zbek tilida, har bir slayd uchun sarlavha va 4-5 nuqta bilan tayyorlang.",
    "kurs": "Siz kurs ishi yozib beradigan yordamchisiz. Kirish, asosiy qism, xulosa, adabiyotlar bilan O'zbek tilida yozing.",
    "maqola": "Siz ilmiy maqola yozib beradigan yordamchisiz. Annotatsiya, kirish, asosiy qism, xulosa bilan O'zbek tilida yozing.",
    "referat": "Siz referat tayyorlab beradigan yordamchisiz. To'liq tuzilma bilan O'zbek tilida yozing.",
    "esse": "Siz esse yozib beradigan yordamchisiz. 500-800 so'z, O'zbek tilida.",
    "test": "Siz A,B,C,D variantli test tuzib beradigan yordamchisiz. To'g'ri javobni oxirida ko'rsating.",
    "tarjima": "Siz professional tarjimon yordamchisiz. So'ralgan tilga aniq tarjima qiling.",
    "umumiy": "Siz O'zbek tilida gaplashadigan talabalar uchun AI yordamchisiz.",
}

NAMES = {
    "slayd": "📊 Slayd", "kurs": "📝 Kurs ishi",
    "maqola": "📄 Maqola", "referat": "📚 Referat",
    "esse": "✍️ Esse", "test": "🧪 Test",
    "tarjima": "🌐 Tarjima", "umumiy": "💬 Suhbat",
}

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")
    def log_message(self, format, *args):
        pass

def run_web():
    server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
    server.serve_forever()

def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Slayd", callback_data="slayd"), InlineKeyboardButton("📝 Kurs ishi", callback_data="kurs")],
        [InlineKeyboardButton("📄 Maqola", callback_data="maqola"), InlineKeyboardButton("📚 Referat", callback_data="referat")],
        [InlineKeyboardButton("✍️ Esse", callback_data="esse"), InlineKeyboardButton("🧪 Test", callback_data="test")],
        [InlineKeyboardButton("🌐 Tarjima", callback_data="tarjima"), InlineKeyboardButton("💬 Suhbat", callback_data="umumiy")],
    ])

def ask(system, text):
    data = json.dumps({
        "model": "claude-opus-4-5",
        "max_tokens": 4000,
        "system": system,
        "messages": [{"role": "user", "content": text}]
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=data,
        headers={
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        },
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())["content"][0]["text"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"👋 Salom *{update.effective_user.first_name}*!\n\n🎓 *Akadem Yordamchi* — talabalar uchun AI!\n\nVazifa tanlang 👇",
        parse_mode="Markdown", reply_markup=menu()
    )

async def btn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "menu":
        user_mode.pop(query.from_user.id, None)
        await query.edit_message_text("🏠 Menyu 👇", reply_markup=menu())
        return
    user_mode[query.from_user.id] = query.data
    await query.edit_message_text(
        f"*{NAMES[query.data]}* rejimi!\n\nMavzuni yozing:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Menyu", callback_data="menu")]])
    )

async def msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    mode = user_mode.get(uid, "umumiy")
    t = await update.message.reply_text(f"⏳ {NAMES[mode]} bajarilmoqda...")
    try:
        res = ask(PROMPTS[mode], update.message.text)
        await t.delete()
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄 Yana", callback_data=mode),
            InlineKeyboardButton("🏠 Menyu", callback_data="menu")
        ]])
        for i in range(0, len(res), 4000):
            chunk = res[i:i+4000]
            await update.message.reply_text(chunk, reply_markup=kb if i+4000 >= len(res) else None)
    except Exception as e:
        logger.error(e)
        await t.edit_text("❌ Xatolik! /start bosing.")

async def menu_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_mode.pop(update.effective_user.id, None)
    await update.message.reply_text("🏠 Menyu 👇", reply_markup=menu())

if __name__ == "__main__":
    t = threading.Thread(target=run_web, daemon=True)
    t.start()
    logger.info(f"Web server {PORT} portda ishga tushdi!")
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu_cmd))
    application.add_handler(CallbackQueryHandler(btn))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, msg))
    logger.info("Bot ishga tushdi!")
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )
