import os
from dotenv import load_dotenv

load_dotenv()

# ============ BOT CONFIG ============
BOT_TOKEN = os.getenv("BOT_TOKEN", "8625557628:AAHeUC2WxfMjJk-RRq3IxTtUJoc0H4XSsAM")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
BOT_USERNAME = "akadem_yordamchi_bot"

# ============ DATABASE ============
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bot_database.db")

# ============ WEBHOOK (for Railway deployment) ============
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
WEBHOOK_PATH = "/webhook/bot"

# ============ PAYMENT GATEWAYS ============

# Payme.uz
PAYME_MERCHANT_ID = os.getenv("PAYME_MERCHANT_ID", "test_merchant")
PAYME_API_KEY = os.getenv("PAYME_API_KEY", "test_key")

# Click.uz
CLICK_SERVICE_ID = os.getenv("CLICK_SERVICE_ID", "28502")
CLICK_MERCHANT_ID = os.getenv("CLICK_MERCHANT_ID", "8000")
CLICK_API_KEY = os.getenv("CLICK_API_KEY", "test_key")

# ============ PRICING ============
FIRST_DOC_PRICE = 0  # First document is FREE

# Next documents prices
NEXT_DOC_PRICE_UZS = 2000  # 2000 UZS
NEXT_DOC_PRICE_USD = 0.17  # 0.17 USD

# ============ DOCUMENT STYLES ============
DOC_STYLES = {
    "apa": "APA Style",
    "harvard": "Harvard Style",
    "uzbek": "O'zbek Standarti"
}

DOC_TYPES = {
    "referat": "Referat (Essay)",
    "kurs": "Kurs Ishi (Coursework)",
    "maqola": "Maqola (Article)",
    "slide": "Slide Presentation"
}

# ============ FEATURE FLAGS ============
ENABLE_QR_CODE = True
ENABLE_TEMPLATES = True
ENABLE_IMAGES = True

# ============ LIMITS ============
MAX_DOCUMENT_SIZE = 1000000  # 1MB in bytes
MAX_TITLE_LENGTH = 200
MAX_CONTENT_LENGTH = 50000  # 50k characters
MAX_DOCUMENTS_PER_DAY = 10  # Free tier limit

# ============ SUPPORT ============
SUPPORT_CHAT_ID = os.getenv("SUPPORT_CHAT_ID", "")
SUPPORT_USERNAME = "akadem_yordamchi_bot"
SUPPORT_EMAIL = "support@akadem.uz"

# ============ LOGGING ============
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "bot.log")

# ============ TIMEZONE ============
TIMEZONE = "Asia/Tashkent"
