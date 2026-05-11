import json
import urllib.request
import urllib.parse
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "8625557628:AAGXuX8xanFU2zoCS5LcXPezhQXsGUP_XQc"
OPENROUTER_API_KEY = "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"
API_URL = f"https://api.telegram.org/bot{TOKEN}"

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

def tg(method, **params):
    data = json.dumps(params).encode()
    req = urllib.request.Request(
        f"{API_URL}/{method}",
        data=data,
        headers={"content-type": "application/json"}
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def ask(system, text):
    data = json.dumps({
        "model": "meta-llama/llama-3.3-70b-instruct:free",
        "max_tokens": 4000,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": text}
        ]
    }).encode()
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=data,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "content-type": "application/json",
            "HTTP-Referer": "https://t.me/akadem_yordamchi_bot",
            "X-Title": "Akadem Yordamchi Bot"
        },
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())["choices"][0]["message"]["content"]

def send_menu(chat_id, text):
    tg("sendMessage",
        chat_id=chat_id,
        text=text,
        parse_mode="Markdown",
        reply_markup={
            "inline_keyboard": [
                [{"text": "📊 Slayd", "callback_data": "slayd"}, {"text": "📝 Kurs ishi", "callback_data": "kurs"}],
                [{"text": "📄 Maqola", "callback_data": "maqola"}, {"text": "📚 Referat", "callback_data": "referat"}],
                [{"text": "✍️ Esse", "callback_data": "esse"}, {"text": "🧪 Test", "callback_data": "test"}],
                [{"text": "🌐 Tarjima", "callback_data": "tarjima"}, {"text": "💬 Suhbat", "callback_data": "umumiy"}],
            ]
        }
    )

def handle_update(update):
    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")
        user_name = update["message"]["from"].get("first_name", "Foydalanuvchi")

        if text == "/start" or text == "/menu":
            user_mode.pop(chat_id, None)
            send_menu(chat_id, f"👋 Salom *{user_name}*!\n\n🎓 *Akadem Yordamchi* — talabalar uchun AI!\n\nVazifa tanlang 👇")
        else:
            mode = user_mode.get(chat_id, "umumiy")
            msg = tg("sendMessage", chat_id=chat_id, text=f"⏳ {NAMES[mode]} bajarilmoqda...")
            msg_id = msg["result"]["message_id"]
            try:
                res = ask(PROMPTS[mode], text)
                tg("deleteMessage", chat_id=chat_id, message_id=msg_id)
                for i in range(0, len(res), 4000):
                    chunk = res[i:i+4000]
                    is_last = i + 4000 >= len(res)
                    if is_last:
                        tg("sendMessage",
                            chat_id=chat_id,
                            text=chunk,
                            reply_markup={
                                "inline_keyboard": [[
                                    {"text": "🔄 Yana", "callback_data": mode},
                                    {"text": "🏠 Menyu", "callback_data": "menu"}
                                ]]
                            }
                        )
                    else:
                        tg("sendMessage", chat_id=chat_id, text=chunk)
            except Exception as e:
                logger.error(f"XATO: {e}")
                tg("editMessageText", chat_id=chat_id, message_id=msg_id, text=f"❌ Xatolik: {str(e)[:200]}")

    elif "callback_query" in update:
        query = update["callback_query"]
        chat_id = query["message"]["chat"]["id"]
        data = query["data"]
        tg("answerCallbackQuery", callback_query_id=query["id"])

        if data == "menu":
            user_mode.pop(chat_id, None)
            tg("editMessageText",
                chat_id=chat_id,
                message_id=query["message"]["message_id"],
                text="🏠 Menyu 👇",
                reply_markup={
                    "inline_keyboard": [
                        [{"text": "📊 Slayd", "callback_data": "slayd"}, {"text": "📝 Kurs ishi", "callback_data": "kurs"}],
                        [{"text": "📄 Maqola", "callback_data": "maqola"}, {"text": "📚 Referat", "callback_data": "referat"}],
                        [{"text": "✍️ Esse", "callback_data": "esse"}, {"text": "🧪 Test", "callback_data": "test"}],
                        [{"text": "🌐 Tarjima", "callback_data": "tarjima"}, {"text": "💬 Suhbat", "callback_data": "umumiy"}],
                    ]
                }
            )
        else:
            user_mode[chat_id] = data
            tg("editMessageText",
                chat_id=chat_id,
                message_id=query["message"]["message_id"],
                text=f"*{NAMES[data]}* rejimi!\n\nMavzuni yozing:",
                parse_mode="Markdown",
                reply_markup={
                    "inline_keyboard": [[{"text": "🏠 Menyu", "callback_data": "menu"}]]
                }
            )

def main():
    offset = 0
    logger.info("Bot ishga tushdi!")
    while True:
        try:
            result = tg("getUpdates", offset=offset, timeout=30)
            for update in result.get("result", []):
                offset = update["update_id"] + 1
                handle_update(update)
        except Exception as e:
            logger.error(f"Xato: {e}")
            time.sleep(3)

if __name__ == "__main__":
    main()
