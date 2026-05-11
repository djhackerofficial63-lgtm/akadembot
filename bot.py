import urllib.request
import urllib.parse
import json
import time

TOKEN = "8625557628:AAGXuX8xanFU2zoCS5LcXPezhQXsGUP_XQc"
OPENROUTER_KEY = "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"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

def tg_request(method, data=None):
    url = f"{BASE_URL}/{method}"
    if data:
        data = json.dumps(data).encode()
        req = urllib.request.Request(url, data=data,
              headers={"Content-Type": "application/json"})
    else:
        req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def send_message(chat_id, text):
    tg_request("sendMessage", {"chat_id": chat_id, "text": text})

def ask_ai(user_message):
    data = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "Siz foydali akademik yordamchisiz. O'zbek tilida javob bering."},
            {"role": "user", "content": user_message}
        ]
    }
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(data).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENROUTER_KEY}"
        }
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        result = json.loads(r.read())
        return result["choices"][0]["message"]["content"]

def main():
    print("✅ Bot ishga tushdi!")
    offset = 0
    while True:
        try:
            result = tg_request("getUpdates", {"offset": offset, "timeout": 25})
            for update in result.get("result", []):
                offset = update["update_id"] + 1
                msg = update.get("message", {})
                chat_id = msg.get("chat", {}).get("id")
                text = msg.get("text", "")
                if not chat_id or not text:
                    continue
                print(f"📩 {chat_id}: {text}")
                if text == "/start":
                    send_message(chat_id, "Salom! Men akademik yordamchiman. Savolingizni yozing!")
                else:
                    send_message(chat_id, "⏳ Javob tayyorlanmoqda...")
                    reply = ask_ai(text)
                    send_message(chat_id, reply)
        except Exception as e:
            print(f"❌ Xato: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
