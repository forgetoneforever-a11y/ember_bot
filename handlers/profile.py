from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from database import get_user

router = Router()

@router.message(Command("profile"))
async def cmd_profile(msg: Message):
    u = await get_user(msg.from_user.id)
    if not u:
        await msg.answer("Ты ещё не зарегистрирован. /start")
        return
    username = f"@{u['username']}" if u["username"] else "скрыт"
    caption = (f"<b>Твоя анкета</b>\n\n"
               f"{u['name']}, {u['age']}\n"
               f"📍 {u['city']}\n"
               f"🔗 {username}\n\n"
               f"{u['bio']}\n\n"
               f"👁 Просмотров: {u['views']}\n"
               f"❤️ Лайков: {u['likes_received']}")
    await msg.answer_photo(u["photo_id"], caption=caption)