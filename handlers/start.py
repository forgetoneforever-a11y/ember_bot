from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states import Reg
from keyboards import gender_kb, looking_kb, search_kb
from database import user_exists, create_user

router = Router()

@router.message(Command("start"))
async def cmd_start(msg: Message, state: FSMContext):
    if await user_exists(msg.from_user.id):
        await msg.answer(
            "Ты уже зарегистрирован! 🎉\n\n"
            "/search — смотреть анкеты\n"
            "/profile — моя анкета\n"
            "/stop — удалить анкету",
            reply_markup=search_kb()
        )
        return
    await msg.answer(
        "Привет! 👋\n\nЭто бот знакомств 16+.\n"
        "Давай создадим анкету.\n\nКак тебя зовут?"
    )
    await state.set_state(Reg.name)

@router.message(Reg.name)
async def reg_name(msg: Message, state: FSMContext):
    if len(msg.text) > 30:
        await msg.answer("Слишком длинное имя, до 30 символов.")
        return
    await state.update_data(name=msg.text)
    await msg.answer("Сколько тебе лет? (только число, минимум 16)")
    await state.set_state(Reg.age)

@router.message(Reg.age)
async def reg_age(msg: Message, state: FSMContext):
    if not msg.text.isdigit() or not (16 <= int(msg.text) <= 99):
        await msg.answer("Введи число от 16 до 99.")
        return
    await state.update_data(age=int(msg.text))
    await msg.answer("Ты кто?", reply_markup=gender_kb())
    await state.set_state(Reg.gender)

@router.callback_query(Reg.gender, F.data.startswith("gender:"))
async def reg_gender(cb: CallbackQuery, state: FSMContext):
    await state.update_data(gender=cb.data.split(":")[1])
    await cb.message.edit_text("Кого ищешь?", reply_markup=looking_kb())
    await state.set_state(Reg.looking)

@router.callback_query(Reg.looking, F.data.startswith("looking:"))
async def reg_looking(cb: CallbackQuery, state: FSMContext):
    await state.update_data(looking_for=cb.data.split(":")[1])
    await cb.message.edit_text("Из какого ты города?")
    await state.set_state(Reg.city)

@router.message(Reg.city)
async def reg_city(msg: Message, state: FSMContext):
    await state.update_data(city=msg.text[:50])
    await msg.answer("Расскажи о себе (до 200 символов).")
    await state.set_state(Reg.bio)

@router.message(Reg.bio)
async def reg_bio(msg: Message, state: FSMContext):
    await state.update_data(bio=msg.text[:200])
    await msg.answer("Отправь своё фото 📸")
    await state.set_state(Reg.photo)

@router.message(Reg.photo, F.photo)
async def reg_photo(msg: Message, state: FSMContext):
    data = await state.get_data()
    data.update({
        "user_id": msg.from_user.id,
        "username": msg.from_user.username,
        "photo_id": msg.photo[-1].file_id,
    })
    await create_user(data)
    await state.clear()
    await msg.answer(
        "Анкета готова! 🎉\n\nНажми, чтобы начать искать:",
        reply_markup=search_kb()
    )

@router.message(Reg.photo)
async def reg_photo_invalid(msg: Message):
    await msg.answer("Нужно именно фото 📸")