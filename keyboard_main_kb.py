from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu():
    """Main menu keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Referat", callback_data="doc_referat")],
        [InlineKeyboardButton(text="📚 Kurs Ishi", callback_data="doc_kurs")],
        [InlineKeyboardButton(text="📄 Maqola", callback_data="doc_maqola")],
        [InlineKeyboardButton(text="🎯 Slide", callback_data="doc_slide")],
        [InlineKeyboardButton(text="💳 Obunani Tekshirish", callback_data="check_sub")],
        [InlineKeyboardButton(text="💰 To'lov Qilish", callback_data="pay_menu")],
    ])

def style_menu():
    """Style selection keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 APA Style", callback_data="style_apa")],
        [InlineKeyboardButton(text="🎯 Harvard Style", callback_data="style_harvard")],
        [InlineKeyboardButton(text="🎯 O'zbek Standarti", callback_data="style_uzbek")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_menu")],
    ])

def payment_menu():
    """Payment gateway selection"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Click.uz", callback_data="pay_click")],
        [InlineKeyboardButton(text="💳 Payme", callback_data="pay_payme")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_menu")],
    ])

def doc_type_menu():
    """Document type selection"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Referat", callback_data="doc_referat")],
        [InlineKeyboardButton(text="📚 Kurs Ishi", callback_data="doc_kurs")],
        [InlineKeyboardButton(text="📄 Maqola", callback_data="doc_maqola")],
        [InlineKeyboardButton(text="🎯 Slide", callback_data="doc_slide")],
    ])

def finish_menu():
    """Document confirmation keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Tugatish va PDF Olish", callback_data="finish_doc")],
        [InlineKeyboardButton(text="➕ Yana Matn Qo'shish", callback_data="add_more_text")],
        [InlineKeyboardButton(text="❌ Bekor Qilish", callback_data="cancel_doc")],
    ])

def admin_menu():
    """Admin control keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats")],
        [InlineKeyboardButton(text="💬 Xabar Yuborish", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="🚫 Foydalanuvchni Bloklash", callback_data="admin_block")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_menu")],
    ])

def currency_menu():
    """Currency selection for payment"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 2,000 UZS", callback_data="cur_uzs")],
        [InlineKeyboardButton(text="🇺🇸 0.17 USD", callback_data="cur_usd")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_menu")],
    ])
