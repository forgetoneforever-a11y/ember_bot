from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from database import (get_user, get_next_profile, add_like,
                      add_view, report_user, deactivate_user)
from keyboards import profile_kb, report_kb, search_kb
from states import Report

router = Router()

def format_profile(u) -> str:
    username = f"@{u['username']}" if u["username"] else "скрыт"
    return (f"<b>{u['name']}, {u['age']}</b>\n"
            f"📍 {u['city']}\n"
            f"🔗 {username}\n\n"
            f"{u['bio']}")

@router.message(Command("search"))
async def cmd_search(msg: Message):
    await show_next(msg, msg.from_user.id)

@router.callback_query(F.data == "search_next")
async def cb_search(cb: CallbackQuery):
    await cb.message.delete()
    await show_next(cb.message, cb.from_user.id, chat_id=cb.from_user.id)

async def show_next(target, user_id: int, chat_id: int = None):
    profile = await get_next_profile(user_id)
    if not profile:
        text = "Пока новых анкет нет 😔 Загляни позже."
        if isinstance(target, Message):
            await target.answer(text, reply_markup=search_kb())
        else:
            await target.bot.send_message(chat_id, text, reply_markup=search_kb())
        return
    await add_view(profile["user_id"])
    kb = profile_kb(profile["user_id"])
    caption = format_profile(profile)
    if isinstance(target, Message):
        await target.answer_photo(profile["photo_id"], caption=caption, reply_markup=kb)
    else:
        await target.bot.send_photo(chat_id, profile["photo_id"], caption=caption, reply_markup=kb)

@router.callback_query(F.data.startswith("skip:"))
async def cb_skip(cb: CallbackQuery):
    await cb.message.delete()
    await show_next(cb.message, cb.from_user.id, chat_id=cb.from_user.id)

@router.callback_query(F.data.startswith("like:"))
async def cb_like(cb: CallbackQuery, bot: Bot):
    to_id = int(cb.data.split(":")[1])
    from_id = cb.from_user.id
    is_match = await add_like(from_id, to_id)

    if is_match:
        me = await get_user(from_id)
        partner = await get_user(to_id)
        # уведомляем партнёра
        try:
            await bot.send_message(
                to_id,
                f"💘 У тебя мэтч с <b>{me['name']}</b>!\n"
                f"Напиши: @{me['username']}" if me['username'] else
                f"💘 У тебя мэтч с <b>{me['name']}</b>!"
            )
        except Exception:
            pass
        partner_username = f"@{partner['username']}" if partner["username"] else partner["name"]
        await cb.answer("Взаимно! 💘")
        await cb.message.answer(f"💘 Взаимный лайк! Напиши: {partner_username}")
        await cb.message.delete()
    else:
        await cb.answer("Лайк отправлен ❤️")
        await cb.message.delete()
    await show_next(cb.message, from_id, chat_id=from_id)

@router.callback_query(F.data.startswith("report:"))
async def cb_report(cb: CallbackQuery, state: FSMContext):
    to_id = int(cb.data.split(":")[1])
    await state.update_data(report_to=to_id)
    await cb.message.edit_reply_markup(reply_markup=report_kb(to_id))

@router.callback_query(F.data.startswith("rep_ok:"))
async def cb_report_reason(cb: CallbackQuery, state: FSMContext):
    _, to_id, reason = cb.data.split(":")
    await report_user(cb.from_user.id, int(to_id), reason)
    await cb.answer("Жалоба отправлена, спасибо!", show_alert=True)
    await cb.message.delete()
    await show_next(cb.message, cb.from_user.id, chat_id=cb.from_user.id)

@router.message(Command("stop"))
async def cmd_stop(msg: Message):
    await deactivate_user(msg.from_user.id)
    await msg.answer("Анкета удалена. /start — создать заново.")