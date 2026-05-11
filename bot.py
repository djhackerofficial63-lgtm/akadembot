import urllib.request
import urllib.parse
import json
import time
import logging
import ssl
import traceback

# =========================
# CONFIG (SHUNI TO‘LDIRASAN)
# =========================

TOKEN = "AAGrTicV7UkzXf-a8_mtMX5fv_JvVXXhpQE"
OPENROUTER_API_KEY = "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"

MODEL = "openai/gpt-4o-mini"

BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"

# =========================
# LOG SYSTEM (DEBUG POWER)
# =========================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

log = logging.getLogger("BOT")

# SSL FIX (Termux uchun)
ssl._create_default_https_context = ssl._create_unverified_context


# =========================
# TELEGRAM CORE
# =========================

def tg(method, data=None):
    url = BASE_URL + method

    if data:
        data = urllib.parse.urlencode(data).encode()

    req = urllib.request.Request(url, data=data)

    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def send(chat_id, text):
    try:
        tg("sendMessage", {
            "chat_id": chat_id,
            "text": str(text)[:4096]
        })
    except Exception as e:
        log.error(f"SEND ERROR: {e}")


def typing(chat_id):
    try:
        tg("sendChatAction", {
            "chat_id": chat_id,
            "action": "typing"
        })
    except:
        pass


def delete_webhook():
    try:
        res = tg("deleteWebhook", {"drop_pending_updates": True})
        log.info(f"Webhook cleared: {res}")
    except Exception as e:
        log.error(f"Webhook error: {e}")


# =========================
# AI FUNCTION (OPENROUTER)
# =========================

def ai(prompt):
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://openrouter.ai",
            "X-Title": "Professional Bot"
        }

        payload = {
            "model": MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "Sen o'zbek tilida aniq va foydali javob beradigan AI assistentsan."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        data = json.dumps(payload).encode()

        req = urllib.request.Request(url, data=data, headers=headers)

        with urllib.request.urlopen(req, timeout=90) as r:
            res = json.loads(r.read())

        return res["choices"][0]["message"]["content"]

    except Exception as e:
        log.error(f"AI ERROR: {e}")
        return "AI ishlamayapti. Key/API tekshiring."


# =========================
# MESSAGE HANDLER
# =========================

def handle(msg):
    try:
        chat_id = msg["chat"]["id"]
        text = msg.get("text", "")

        log.info(f"MSG: {text}")

        if text == "/start":
            send(chat_id, "Salom! Men AI botman 🤖")
            return

        if text == "/help":
            send(chat_id, "Savol yubor — men javob beraman.")
            return

        if not text:
            send(chat_id, "Faqat matn yuboring.")
            return

        typing(chat_id)

        answer = ai(text)

        send(chat_id, answer)

    except Exception as e:
        log.error(f"HANDLER ERROR: {e}")
        traceback.print_exc()


# =========================
# MAIN LOOP (STABLE + AUTO RECOVER)
# =========================

def main():
    log.info("BOT STARTING...")

    delete_webhook()

    offset = 0

    while True:
        try:
            updates = tg("getUpdates", {"timeout": 30, "offset": offset})

            if updates.get("ok"):

                for u in updates["result"]:
                    offset = u["update_id"] + 1

                    if "message" in u:
                        handle(u["message"])

            time.sleep(1)

        except KeyboardInterrupt:
            log.info("STOPPED BY USER")
            break

        except Exception as e:
            log.error(f"LOOP ERROR: {e}")
            time.sleep(3)


# =========================
# RUN
# =========================

if __name__ == "__main__":
    main()
