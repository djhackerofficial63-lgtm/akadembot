import urllib.request
import urllib.parse
import json
import time
import logging
import ssl

# =========================
# CONFIG
# =========================

TOKEN = "PASTE_NEW_BOT_TOKEN"
OPENROUTER_API_KEY = "PASTE_NEW_OPENROUTER_KEY"

MODEL = "openai/gpt-4o-mini"

BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"

# =========================
# LOGGING
# =========================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# =========================
# SSL FIX
# =========================

ssl._create_default_https_context = ssl._create_unverified_context

# =========================
# TELEGRAM FUNCTIONS
# =========================

def delete_webhook():
    try:
        url = BASE_URL + "deleteWebhook"

        with urllib.request.urlopen(url) as response:
            result = json.loads(response.read())

        logger.info(f"Webhook deleted: {result}")

    except Exception as e:
        logger.error(f"Webhook delete error: {e}")


def get_updates(offset):
    url = BASE_URL + f"getUpdates?timeout=30&offset={offset}"

    with urllib.request.urlopen(url, timeout=35) as response:
        data = response.read()

    return json.loads(data)


def send_message(chat_id, text):
    try:
        message = str(text)[:4000]

        data = urllib.parse.urlencode({
            "chat_id": chat_id,
            "text": message
        }).encode()

        req = urllib.request.Request(
            BASE_URL + "sendMessage",
            data=data
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            return response.read()

    except Exception as e:
        logger.error(f"Send message error: {e}")


def send_typing(chat_id):
    try:
        data = urllib.parse.urlencode({
            "chat_id": chat_id,
            "action": "typing"
        }).encode()

        req = urllib.request.Request(
            BASE_URL + "sendChatAction",
            data=data
        )

        urllib.request.urlopen(req, timeout=10)

    except:
        pass

# =========================
# OPENROUTER AI
# =========================

def ask_ai(prompt):
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://openrouter.ai",
            "X-Title": "Akadem Bot"
        }

        payload = {
            "model": MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful Uzbek AI assistant for students. "
                        "Answer clearly and shortly."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        data = json.dumps(payload).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=data,
            headers=headers,
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read())

        return result["choices"][0]["message"]["content"]

    except Exception as e:
        logger.error(f"AI error: {e}")
        return "AI bilan bog‘lanishda xatolik bo‘ldi."

# =========================
# MESSAGE HANDLER
# =========================

def handle_message(message):
    try:
        chat_id = message["chat"]["id"]

        text = message.get("text", "")

        logger.info(f"Message: {text}")

        # START COMMAND
        if text == "/start":
            send_message(
                chat_id,
                "Salom! Men Akadem AI botman.\n\nSavolingizni yuboring."
            )
            return

        # HELP COMMAND
        if text == "/help":
            send_message(
                chat_id,
                "Menga istalgan savol yuboring.\n"
                "Men AI yordamida javob beraman."
            )
            return

        # EMPTY MESSAGE
        if not text:
            send_message(chat_id, "Faqat text yuboring.")
            return

        send_typing(chat_id)

        answer = ask_ai(text)

        send_message(chat_id, answer)

    except Exception as e:
        logger.error(f"Handle message error: {e}")

# =========================
# MAIN LOOP
# =========================

def main():
    logger.info("Bot starting...")

    delete_webhook()

    offset = 0

    while True:
        try:
            updates = get_updates(offset)

            if updates.get("ok"):

                for update in updates["result"]:

                    offset = update["update_id"] + 1

                    if "message" in update:
                        handle_message(update["message"])

            time.sleep(1)

        except KeyboardInterrupt:
            logger.info("Bot stopped")
            break

        except Exception as e:
            logger.error(f"Main loop error: {e}")
            time.sleep(5)

# =========================
# START
# =========================

if __name__ == "__main__":
    main()
