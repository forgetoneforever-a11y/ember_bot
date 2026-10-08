from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def gender_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="👦 Парень", callback_data="gender:male"),
        InlineKeyboardButton(text="👧 Девушка", callback_data="gender:female"),
    ]])

def looking_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="👦 Парней", callback_data="looking:male"),
        InlineKeyboardButton(text="👧 Девушек", callback_data="looking:female"),
    ]])

def profile_kb(user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="❤️", callback_data=f"like:{user_id}"),
        InlineKeyboardButton(text="👎", callback_data=f"skip:{user_id}"),
        InlineKeyboardButton(text="⚠️ Жалоба", callback_data=f"report:{user_id}"),
    ]])

def report_kb(user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Спам", callback_data=f"rep_ok:{user_id}:spam")],
        [InlineKeyboardButton(text="18+ контент", callback_data=f"rep_ok:{user_id}:adult")],
        [InlineKeyboardButton(text="Оскорбления", callback_data=f"rep_ok:{user_id}:insult")],
        [InlineKeyboardButton(text="Другое", callback_data=f"rep_ok:{user_id}:other")],
    ])

def search_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🔍 Смотреть анкеты", callback_data="search_next"),
    ]])