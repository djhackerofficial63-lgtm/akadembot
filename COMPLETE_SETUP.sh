#!/bin/bash

# AKADEM YORDAMCHI BOT - COMPLETE SETUP
# Copy and paste this entire script in Termux

echo "🚀 AKADEM BOT COMPLETE SETUP"
echo "=============================="

# Navigate to home
cd ~

# Create main folder
mkdir -p akadem_yordamchi_bot
cd akadem_yordamchi_bot

# Create subfolders
mkdir -p keyboards
mkdir -p services
mkdir -p documents

echo "✅ Folders created"

# ============ Create bot.py ============
cat > bot.py << 'BOTEOF'
import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import BotCommand, Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime

from config import BOT_TOKEN, ADMIN_ID
from database import init_db, get_session, User, Document
from keyboards.main_kb import main_menu, style_menu, finish_menu
from services.document_generator import DocumentGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentStates(StatesGroup):
    choosing_type = State()
    choosing_style = State()
    writing_title = State()
    writing_content = State()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
doc_gen = DocumentGenerator()

@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    session = get_session()
    user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
    
    if not user:
        user = User(
            telegram_id=message.from_user.id,
            username=message.from_user.username or "unknown",
            first_name=message.from_user.first_name or "User",
            created_at=datetime.utcnow()
        )
        session.add(user)
        session.commit()
    
    welcome = """
🎓 **Akademik Yordamchi Botga Xush Kelibsiz!**

Siz quyidagi hujjatlarni yarata olasiz:
📝 **Referat**
📚 **Kurs Ishi**
📄 **Maqola**
🎯 **Slide**

💡 Birinchi hujjat TEKIN!
    """
    
    await message.answer(welcome, reply_markup=main_menu())
    session.close()

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("📖 Qo'llanma:\n1. Hujjat turini tanlang\n2. Uslubni tanlang\n3. Matnni yuboring\n4. PDF olasiz!", reply_markup=main_menu())

@dp.callback_query(F.data.startswith("doc_"))
async def process_doc(callback: CallbackQuery, state: FSMContext):
    doc_type = callback.data.replace("doc_", "")
    await state.update_data(doc_type=doc_type)
    await callback.message.edit_text("📋 Uslubni tanlang:", reply_markup=style_menu())
    await state.set_state(DocumentStates.choosing_style)

@dp.callback_query(F.data.startswith("style_"))
async def process_style(callback: CallbackQuery, state: FSMContext):
    style = callback.data.replace("style_", "")
    await state.update_data(style=style)
    await callback.message.edit_text("✏️ Sarlavhani yuboring:")
    await state.set_state(DocumentStates.writing_title)

@dp.message(DocumentStates.writing_title)
async def process_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("📝 Matnni yuboring:")
    await state.set_state(DocumentStates.writing_content)

@dp.message(DocumentStates.writing_content)
async def process_content(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(content=message.text)
    await message.answer("✅ Matn qabul qilindi!\n\n🔄 Yana qo'shib olasiz yoki tugatish uchun /finish", reply_markup=finish_menu())

@dp.message(Command("finish"))
async def finish_doc(message: Message, state: FSMContext):
    data = await state.get_data()
    session = get_session()
    
    try:
        doc_path = doc_gen.generate_document(
            doc_type=data['doc_type'],
            style=data['style'],
            title=data['title'],
            content=data['content'],
            user_id=message.from_user.id
        )
        
        document = Document(
            user_id=message.from_user.id,
            doc_type=data['doc_type'],
            template_style=data['style'],
            title=data['title'],
            content=data['content'],
            file_path=doc_path,
            created_at=datetime.utcnow()
        )
        
        session.add(document)
        session.commit()
        
        with open(doc_path, 'rb') as file:
            await message.answer_document(file, caption="✅ Hujjat tayyorlandi!")
        
        await state.clear()
        await message.answer("🎉 Boshqa hujjat yaratmoqchimisiz?", reply_markup=main_menu())
        
    except Exception as e:
        await message.answer(f"❌ Xatolik: {str(e)}", reply_markup=main_menu())
    finally:
        session.close()

@dp.message()
async def echo(message: Message):
    await message.answer("❓ Tushunmadim! /help buyrug'idan foydalaning.", reply_markup=main_menu())

async def main():
    logger.info("🚀 Bot ishga tushmoqda...")
    init_db()
    
    commands = [
        BotCommand(command="start", description="Botni boshlash"),
        BotCommand(command="help", description="Yordam"),
        BotCommand(command="finish", description="Hujjatni tugatish"),
    ]
    await bot.set_my_commands(commands)
    logger.info("✅ Bot ishga tushdi!")
    
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"❌ Xatolik: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️ Bot to'xtatildi")
BOTEOF

echo "✅ bot.py created"

# ============ Create config.py ============
cat > config.py << 'CFGEOF'
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "8625557628:AAHeUC2WxfMjJk-RRq3IxTtUJoc0H4XSsAM")
ADMIN_ID = int(os.getenv("ADMIN_ID", "7758296066"))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bot_database.db")

DOC_STYLES = {
    "apa": "APA Style",
    "harvard": "Harvard Style",
    "uzbek": "O'zbek Standarti"
}

DOC_TYPES = {
    "referat": "Referat",
    "kurs": "Kurs Ishi",
    "maqola": "Maqola",
    "slide": "Slide"
}
CFGEOF

echo "✅ config.py created"

# ============ Create database.py ============
cat > database.py << 'DBEOF'
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL
from datetime import datetime

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    username = Column(String)
    first_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    doc_type = Column(String)
    template_style = Column(String)
    title = Column(String)
    content = Column(Text)
    file_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(engine)

def init_db():
    Base.metadata.create_all(engine)

def get_session():
    return SessionLocal()
DBEOF

echo "✅ database.py created"

# ============ Create .env ============
cat > .env << 'ENVEOF'
BOT_TOKEN=8625557628:AAHeUC2WxfMjJk-RRq3IxTtUJoc0H4XSsAM
ADMIN_ID=7758296066
DATABASE_URL=sqlite:///bot_database.db
ENVEOF

echo "✅ .env created"

# ============ Create requirements.txt ============
cat > requirements.txt << 'REQEOF'
aiogram==3.0.0
python-dotenv==1.0.0
sqlalchemy==2.0.23
aiosqlite==3.1.1
reportlab==4.0.7
qrcode==7.4.2
pillow==10.0.1
REQEOF

echo "✅ requirements.txt created"

# ============ Create keyboards/__init__.py ============
cat > keyboards/__init__.py << 'KBEOF'
# Keyboards package
KBEOF

echo "✅ keyboards/__init__.py created"

# ============ Create keyboards/main_kb.py ============
cat > keyboards/main_kb.py << 'KBMEOF'
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Referat", callback_data="doc_referat")],
        [InlineKeyboardButton(text="📚 Kurs Ishi", callback_data="doc_kurs")],
        [InlineKeyboardButton(text="📄 Maqola", callback_data="doc_maqola")],
        [InlineKeyboardButton(text="🎯 Slide", callback_data="doc_slide")],
    ])

def style_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="APA", callback_data="style_apa")],
        [InlineKeyboardButton(text="Harvard", callback_data="style_harvard")],
        [InlineKeyboardButton(text="Uzbek", callback_data="style_uzbek")],
    ])

def finish_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Tugatish", callback_data="finish_doc")],
        [InlineKeyboardButton(text="➕ Yana qo'shish", callback_data="add_more")],
    ])
KBMEOF

echo "✅ keyboards/main_kb.py created"

# ============ Create services/__init__.py ============
cat > services/__init__.py << 'SRVEOF'
# Services package
SRVEOF

echo "✅ services/__init__.py created"

# ============ Create services/document_generator.py ============
cat > services/document_generator.py << 'DOCEOF'
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from datetime import datetime
from pathlib import Path
import qrcode
import logging

logger = logging.getLogger(__name__)

class DocumentGenerator:
    def __init__(self):
        self.output_dir = Path("documents")
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_document(self, doc_type, style, title, content, user_id):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.output_dir}/{user_id}_{doc_type}_{timestamp}.pdf"
            
            doc = SimpleDocTemplate(filename, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            story.append(Paragraph(title, styles['Heading1']))
            story.append(Spacer(1, 0.5*inch))
            
            # Content
            paragraphs = content.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    story.append(Paragraph(para.strip(), styles['BodyText']))
                    story.append(Spacer(1, 0.2*inch))
            
            doc.build(story)
            logger.info(f"✅ Document generated: {filename}")
            return filename
        
        except Exception as e:
            logger.error(f"Error generating document: {e}")
            return None
DOCEOF

echo "✅ services/document_generator.py created"

# ============ Create services/payment_service.py ============
cat > services/payment_service.py << 'PAYEOF'
import logging

logger = logging.getLogger(__name__)

class PaymentService:
    def __init__(self):
        self.click_api_url = "https://api.click.uz/v2"
        self.payme_api_url = "https://checkout.paycom.uz/api"
    
    def get_payment_link(self, user_id, amount, currency, gateway):
        logger.info(f"Payment requested: {amount} {currency} via {gateway}")
        return f"https://payment.link/{gateway}/{amount}"
PAYEOF

echo "✅ services/payment_service.py created"

# ============ Summary ============
echo ""
echo "=============================="
echo "✅ ALL FILES CREATED!"
echo "=============================="
echo ""
echo "Folder structure:"
ls -la
echo ""
echo "keyboards/:"
ls keyboards/
echo ""
echo "services/:"
ls services/
echo ""
echo "=============================="
echo "🚀 NEXT STEPS:"
echo "=============================="
echo ""
echo "1. pip install -r requirements.txt"
echo "2. python bot.py"
echo "3. Then:"
echo "   git add ."
echo "   git commit -m 'Complete bot setup'"
echo "   git push"
echo ""
echo "✅ DONE!"
