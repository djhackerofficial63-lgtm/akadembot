import os
import json
import urllib.request
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from aiohttp import web

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "8625557628:AAGXuX8xanFU2zoCS5LcXPezhQXsGUP_XQc"
TOGETHER_API_KEY = "tgp_v1_8QBA51Bhw5VIR2X8FrREJpReZCd6elFLmXs9whDnI68"
PORT = int(os.environ.get("PORT", 8080))
WEBHOOK_URL = "https://akadembot-1.onrender.com"
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

def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Slayd", callback_data="slayd"), InlineKeyboardButton("📝 Kurs ishi", callback_data="kurs")],
        [InlineKeyboardButton("📄 Maqola", callback_data="maqola"), InlineKeyboardButton("📚 Referat", callback_data="referat")],
        [InlineKeyboardButton("✍️ Esse", callback_data="esse"), InlineKeyboardButton("🧪 Test", callback_data="test")],
        [InlineKeyboardButton("🌐 Tarjima", callback_data="tarjima"), InlineKeyboardButton("💬 Suhbat", callback_data="umumiy")],
    ])

def ask(system, text):
    data = json.dumps({
        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        "max_tokens": 4000,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": text}
        ]
    }).encode()
    req = urllib.request.Request(
        "https://api.together.xyz/v1/chat/completions",
        data=data,
        headers={
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "content-type": "application/json"
        },
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())["choices"][0]["message"]["content"]

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
        logger.error(f"XATO: {type(e).__name__}: {e}")
        await t.edit_text(f"❌ Xatolik: {type(e).__name__}: {str(e)[:200]}")

async def menu_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_mode.pop(update.effective_user.id, None)
    await update.message.reply_text("🏠 Menyu 👇", reply_markup=menu())

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu_cmd))
    app.add_handler(CallbackQueryHandler(btn))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, msg))

    await app.bot.set_webhook(
        url=f"{WEBHOOK_URL}/{TOKEN}",
        drop_pending_updates=True
    )
    await app.initialize()
    await app.start()

    async def handle(request):
        data = await request.json()
        update = Update.de_json(data, app.bot)
        await app.process_update(update)
        return web.Response(text="OK")

    async def health(request):
        return web.Response(text="Bot is running!")

    server = web.Application()
    server.router.add_post(f"/{TOKEN}", handle)
    server.router.add_get("/", health)

    runner = web.AppRunner(server)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    logger.info("Bot ishga tushdi!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
