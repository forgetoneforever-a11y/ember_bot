from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from config import ADMIN_IDS

router = Router()

@router.message(Command("admin"))
async def cmd_admin(msg: Message):
    if msg.from_user.id not in ADMIN_IDS:
        return
    await msg.answer(
        "Админ-панель доступна на сайте.\n"
        "Команды:\n"
        "/ban <user_id> — деактивировать анкету\n"
    )

@router.message(Command("ban"))
async def cmd_ban(msg: Message):
    if msg.from_user.id not in ADMIN_IDS:
        return
    parts = msg.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        await msg.answer("Использование: /ban <user_id>")
        return
    from database import deactivate_user
    await deactivate_user(int(parts[1]))
    await msg.answer(f"Пользователь {parts[1]} деактивирован.")
