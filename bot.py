import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import BotCommand, Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import sys
import os
from datetime import datetime, timedelta

# Import custom modules
from config import BOT_TOKEN, ADMIN_ID, DATABASE_URL
from database import init_db, get_session, User, Document, Payment
from keyboards.main_kb import main_menu, style_menu, payment_menu, doc_type_menu
from services.document_generator import DocumentGenerator
from services.payment_service import PaymentService

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FSM States
class DocumentStates(StatesGroup):
    choosing_type = State()
    choosing_style = State()
    writing_title = State()
    writing_content = State()
    confirming = State()

class PaymentStates(StatesGroup):
    choosing_gateway = State()
    processing = State()

# Initialize bot
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Services
doc_gen = DocumentGenerator()
payment_service = PaymentService()

# ============ COMMAND HANDLERS ============

@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Start command - greet user and create profile if new"""
    session = get_session()
    
    try:
        user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
        
        if not user:
            user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username or "unknown",
                first_name=message.from_user.first_name or "User",
                language="uz",
                first_doc_used=False,
                created_at=datetime.utcnow()
            )
            session.add(user)
            session.commit()
            logger.info(f"✅ New user created: {message.from_user.id}")
        
        welcome_text = """
🎓 **Akademik Yordamchi Botga Xush Kelibsiz!**

Siz quyidagi hujjatlarni yarata olasiz:
📝 **Referat** - Kichik tadqiqot ishi
📚 **Kurs Ishi** - Kurs oxirida topshirish
📄 **Maqola** - Ilmiy maqola
🎯 **Slide** - Prezentasiya

💡 **Birinchi hujjatingiz TEKIN!**
Keyingisini yaratish uchun to'lov qilish kerak (2,000 UZS yoki 0.17 USD)

🔥 Qanday hujjat yaratmoqchisiz?
        """
        
        await message.answer(welcome_text, reply_markup=main_menu())
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await message.answer("❌ Xatolik yuz berdi. Qayta urinib ko'ring.")
    finally:
        session.close()

@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Help command"""
    help_text = """
📖 **Qo'llanma:**

**1️⃣ Hujjat Yaratish:**
   - Hujjat turini tanlang
   - Uslubni tanlang (APA/Harvard/Uzbek)
   - Sarlavha yuboring
   - Matnni yuboring
   - PDF olasiz!

**2️⃣ Uslublar:**
   🎯 **APA** - Ilmiy ishlari uchun
   🎯 **Harvard** - Britaniyaga qo'l tutadi
   🎯 **Uzbek** - O'zbek standartiga

**3️⃣ Obuna:**
   - Birinchi hujjat TEKIN
   - Keyingilari 2,000 UZS (0.17 USD)
   - Click.uz yoki Payme orqali to'lang

**4️⃣ Qo'shimcha:**
   - QR kod avtomatik qo'shiladi
   - Rasm qo'shish mumkin
   - Template-lar mavjud

❓ Muammosi bo'lsa, admin bilan bog'laning: @akadem_yordamchi_bot
    """
    await message.answer(help_text, reply_markup=main_menu())

@dp.message(Command("admin"))
async def cmd_admin(message: Message):
    """Admin panel"""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Siz admin emassiz!")
        return
    
    admin_text = """
👨‍💼 **ADMIN PANEL**

📊 Statistika:
/stats - Foydalanuvchilar soni
/payments - To'lovlar tarixi

⚙️ Boshqaruv:
/broadcast - Xabar yuborish
/block - Foydalanuvchini bloklash
/unblock - Blokirni olib tashlash
    """
    await message.answer(admin_text)

# ============ CALLBACK HANDLERS ============

@dp.callback_query(F.data.startswith("doc_"))
async def process_doc_type(callback: CallbackQuery, state: FSMContext):
    """Handle document type selection"""
    doc_type = callback.data.replace("doc_", "")
    
    doc_types = {
        "referat": "📝 Referat",
        "kurs": "📚 Kurs Ishi",
        "maqola": "📄 Maqola",
        "slide": "🎯 Slide"
    }
    
    if doc_type not in doc_types:
        await callback.answer("❌ Noto'g'ri tur!")
        return
    
    session = get_session()
    user = session.query(User).filter_by(telegram_id=callback.from_user.id).first()
    session.close()
    
    if not user:
        await callback.answer("❌ Foydalanuvchi topilmadi!")
        return
    
    # Check if user has free doc
    if user.first_doc_used:
        await callback.answer("💰 Avval to'lovni qilishingiz kerak!", show_alert=True)
        await callback.message.edit_text(
            "💳 To'lov usulini tanlang:",
            reply_markup=payment_menu()
        )
        return
    
    await state.update_data(doc_type=doc_type)
    await callback.message.edit_text(
        f"✅ Siz {doc_types[doc_type]} turini tanladingiz\n\n"
        "📋 Endi uslubni tanlang:",
        reply_markup=style_menu()
    )
    await state.set_state(DocumentStates.choosing_style)
    await callback.answer()

@dp.callback_query(F.data.startswith("style_"))
async def process_style(callback: CallbackQuery, state: FSMContext):
    """Handle style selection"""
    style = callback.data.replace("style_", "")
    
    styles = {
        "apa": "APA Style",
        "harvard": "Harvard Style",
        "uzbek": "O'zbek Standarti"
    }
    
    if style not in styles:
        await callback.answer("❌ Noto'g'ri uslub!")
        return
    
    await state.update_data(style=style)
    await callback.message.edit_text(
        f"✅ Siz {styles[style]} ni tanladingiz\n\n"
        "✏️ Endi hujjatning **sarlavhasini** yuboring:"
    )
    await state.set_state(DocumentStates.writing_title)
    await callback.answer()

@dp.message(DocumentStates.writing_title)
async def process_title(message: Message, state: FSMContext):
    """Handle title input"""
    if len(message.text) < 3 or len(message.text) > 200:
        await message.answer("❌ Sarlavha 3 dan 200 ta belgigacha bo'lishi kerak!")
        return
    
    await state.update_data(title=message.text)
    await message.answer(
        f"✅ Sarlavha qabul qilindi: **{message.text}**\n\n"
        "📝 Endi **matnni** yuboring:\n"
        "(Uzun bo'lsa, bir nechta xabarda yuboring)"
    )
    await state.set_state(DocumentStates.writing_content)

@dp.message(DocumentStates.writing_content)
async def process_content(message: Message, state: FSMContext):
    """Handle content input"""
    data = await state.get_data()
    
    if "content" in data:
        # Append to existing content
        data["content"] += "\n\n" + message.text
    else:
        data["content"] = message.text
    
    await state.update_data(content=data["content"])
    
    await message.answer(
        "✅ Matn qabul qilindi!\n\n"
        "📊 Hujjat ma'lumotlari:\n"
        f"📝 Tur: {data['doc_type']}\n"
        f"📋 Uslub: {data['style']}\n"
        f"📖 Sarlavha: {data['title']}\n"
        f"📄 Tekst hajmi: {len(data['content'])} belgi\n\n"
        "🔄 Yana matn qo'shib olasiz yoki **Tugatish** tugmasini bosing.",
        reply_markup=finish_menu()
    )

@dp.callback_query(F.data == "finish_doc")
async def finish_document(callback: CallbackQuery, state: FSMContext):
    """Finish document creation and generate"""
    await callback.message.edit_text("⏳ Hujjat yaratilmoqda...", reply_markup=None)
    
    data = await state.get_data()
    session = get_session()
    
    try:
        # Generate document
        doc_path = doc_gen.generate_document(
            doc_type=data['doc_type'],
            style=data['style'],
            title=data['title'],
            content=data['content'],
            user_id=callback.from_user.id
        )
        
        # Save to database
        document = Document(
            user_id=callback.from_user.id,
            doc_type=data['doc_type'],
            template_style=data['style'],
            title=data['title'],
            content=data['content'],
            file_path=doc_path,
            created_at=datetime.utcnow()
        )
        
        user = session.query(User).filter_by(telegram_id=callback.from_user.id).first()
        user.first_doc_used = True
        
        session.add(document)
        session.commit()
        
        logger.info(f"✅ Document created for user {callback.from_user.id}")
        
        # Send file
        with open(doc_path, 'rb') as file:
            await callback.message.answer_document(
                file,
                caption=f"✅ Hujjat tayyorlandi!\n\n"
                        f"📝 Tur: {data['doc_type']}\n"
                        f"📋 Uslub: {data['style']}\n"
                        f"📖 Sarlavha: {data['title']}\n\n"
                        f"🎁 Birinchi hujjatingiz tekin edi!\n"
                        f"Keyingisini yaratish uchun obuna olish kerak (2,000 UZS)"
            )
        
        await state.clear()
        await callback.message.answer(
            "🎉 Boshqa hujjat yaratmoqchimisiz?",
            reply_markup=main_menu()
        )
        
    except Exception as e:
        logger.error(f"Error generating document: {e}")
        await callback.message.answer(
            "❌ Xatolik yuz berdi!\n" + str(e),
            reply_markup=main_menu()
        )
    finally:
        session.close()

@dp.callback_query(F.data.startswith("pay_"))
async def process_payment(callback: CallbackQuery, state: FSMContext):
    """Handle payment gateway selection"""
    gateway = callback.data.replace("pay_", "")
    
    if gateway == "click":
        payment_text = """
💳 **Click.uz orqali to'lov**

2,000 UZS = 0.17 USD

Quydagi kartalarni qabul qiladi:
✅ Humo
✅ Visa
✅ Mastercard

🔗 To'lovni amalga oshirish uchun bosing:
        """
        await callback.message.edit_text(payment_text)
        # Add actual Click payment link
        
    elif gateway == "payme":
        payment_text = """
💳 **Payme orqali to'lov**

2,000 UZS = 0.17 USD

Quydagi kartalarni qabul qiladi:
✅ Humo
✅ Visa
✅ Mastercard

🔗 To'lovni amalga oshirish uchun bosing:
        """
        await callback.message.edit_text(payment_text)
        # Add actual Payme payment link
    
    await callback.answer("⏳ To'lov linki tayyorlanmoqda...")

@dp.callback_query(F.data == "check_sub")
async def check_subscription(callback: CallbackQuery):
    """Check user subscription status"""
    session = get_session()
    user = session.query(User).filter_by(telegram_id=callback.from_user.id).first()
    session.close()
    
    if not user:
        await callback.answer("❌ Foydalanuvchi topilmadi!", show_alert=True)
        return
    
    sub_text = f"""
📊 **OBUNA HOLATI**

👤 Foydalanuvchi: {user.first_name}
📅 Ro'yxatga olingan: {user.created_at.strftime('%d.%m.%Y')}

🎁 Birinchi hujjat: {'✅ Ishlatildi' if user.first_doc_used else '⏳ Ishlatilmadi (TEKIN)'}

📄 Yaratilgan hujjatlar: {len(session.query(Document).filter_by(user_id=user.telegram_id).all())}

💰 To'lov uchun: /payment
    """
    
    await callback.message.edit_text(sub_text, reply_markup=main_menu())
    await callback.answer()

# ============ ERROR HANDLER ============

@dp.message()
async def echo(message: Message):
    """Default handler for unknown messages"""
    await message.answer(
        "❓ Tushunmadim! Quyidagi buyruqlardan foydalaning:\n"
        "/start - Botni boshlash\n"
        "/help - Yordam\n"
        "/admin - Admin panel",
        reply_markup=main_menu()
    )

# ============ MAIN FUNCTION ============

async def main():
    """Main function - start polling"""
    logger.info("🚀 Bot ishga tushmoqda...")
    
    # Initialize database
    init_db()
    logger.info("✅ Database tayyorlandi")
    
    # Set bot commands
    commands = [
        BotCommand(command="start", description="Botni boshlash"),
        BotCommand(command="help", description="Yordam"),
        BotCommand(command="admin", description="Admin panel"),
    ]
    await bot.set_my_commands(commands)
    logger.info("✅ Bot buyruqlari o'rnatildi")
    
    # Start polling
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"❌ Bot xatosi: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️ Bot to'xtatildi")
