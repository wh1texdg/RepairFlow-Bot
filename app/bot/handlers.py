import logging
from datetime import date
from decimal import Decimal, InvalidOperation

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot.keyboards import (
    cancel_keyboard,
    confirmation_keyboard,
    main_menu,
    object_keyboard,
    repair_keyboard,
)
from app.bot.states import RequestForm
from app.core.config import settings
from app.database.session import AsyncSessionLocal
from app.integrations.google_sheets import GoogleSheetsService
from app.integrations.notifications import NotificationService
from app.services.request_service import RequestService
from app.services.user_service import UserService

logger = logging.getLogger(__name__)
router = Router()

OBJECT_LABELS = {
    "apartment": "Вся квартира",
    "kitchen": "Кухня",
    "bathroom": "Ванная",
    "room": "Комната",
    "other": "Другое",
}
REPAIR_LABELS = {
    "cosmetic": "Косметический",
    "capital": "Капитальный",
    "designer": "Дизайнерский",
    "undecided": "Не определился",
}


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    async with AsyncSessionLocal() as session:
        service = UserService(session)
        await service.get_or_create_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
        )
        await session.commit()
    await message.answer(
        "Добро пожаловать в RepairFlow.\nВыберите действие:",
        reply_markup=main_menu(),
    )


@router.message(Command("help"))
@router.message(F.text == "Помощь")
async def help_handler(message: Message):
    await message.answer(
        "RepairFlow собирает заявку на ремонт и передаёт её менеджеру.\n"
        "Нажмите «Новая заявка», чтобы начать."
    )


@router.message(Command("cancel"))
@router.message(F.text == "Отмена")
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Заявка отменена.", reply_markup=main_menu())


@router.message(Command("new_request"))
@router.message(F.text == "Новая заявка")
async def new_request(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(RequestForm.object_type)
    await message.answer("Что нужно отремонтировать?", reply_markup=object_keyboard())


@router.callback_query(RequestForm.object_type, F.data.startswith("object:"))
async def object_type(callback: CallbackQuery, state: FSMContext):
    value = callback.data.split(":", 1)[1]
    await state.update_data(object_type=value)
    await state.set_state(RequestForm.repair_type)
    await callback.message.edit_text("Какой тип ремонта?", reply_markup=repair_keyboard())
    await callback.answer()


@router.callback_query(RequestForm.repair_type, F.data.startswith("repair:"))
async def repair_type(callback: CallbackQuery, state: FSMContext):
    value = callback.data.split(":", 1)[1]
    await state.update_data(repair_type=value)
    await state.set_state(RequestForm.area)
    await callback.message.edit_text("Укажите примерную площадь в м².")
    await callback.answer()


@router.message(RequestForm.area)
async def area(message: Message, state: FSMContext):
    try:
        value = Decimal(message.text.replace(",", "."))
    except (InvalidOperation, AttributeError):
        await message.answer("Введите площадь числом, например: 62.5")
        return
    if value <= 0 or value > 10000:
        await message.answer("Площадь должна быть больше 0 и не больше 10000 м².")
        return
    await state.update_data(area=str(value))
    await state.set_state(RequestForm.location)
    await message.answer("Напишите город и адрес.")


@router.message(RequestForm.location)
async def location(message: Message, state: FSMContext):
    await state.update_data(location=message.text.strip())
    await state.set_state(RequestForm.budget)
    await message.answer("Укажите бюджет в рублях. Если бюджет неизвестен — напишите 0.")


@router.message(RequestForm.budget)
async def budget(message: Message, state: FSMContext):
    try:
        value = Decimal(message.text.replace(" ", "").replace(",", "."))
    except (InvalidOperation, AttributeError):
        await message.answer("Введите бюджет числом.")
        return
    if value < 0:
        await message.answer("Бюджет не может быть отрицательным.")
        return
    await state.update_data(budget=str(value))
    await state.set_state(RequestForm.start_date)
    await message.answer("Когда хотите начать ремонт? Формат: ДД.ММ.ГГГГ")


@router.message(RequestForm.start_date)
async def start_date(message: Message, state: FSMContext):
    try:
        value = date.fromisoformat(".".join(reversed(message.text.strip().split("."))))
    except (ValueError, AttributeError):
        await message.answer("Введите дату в формате ДД.ММ.ГГГГ.")
        return
    if value < date.today():
        await message.answer("Дата начала не может быть в прошлом.")
        return
    await state.update_data(start_date=value.isoformat())
    await state.set_state(RequestForm.name)
    await message.answer("Как вас зовут?")


@router.message(RequestForm.name)
async def name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(RequestForm.phone)
    await message.answer("Укажите номер телефона.")


@router.message(RequestForm.phone)
async def phone(message: Message, state: FSMContext):
    value = message.text.strip()
    digits = "".join(ch for ch in value if ch.isdigit())
    if len(digits) < 10 or len(digits) > 15:
        await message.answer("Проверьте номер телефона и попробуйте ещё раз.")
        return
    await state.update_data(phone=value)
    await state.set_state(RequestForm.confirmation)

    data = await state.get_data()
    city, _, address = data["location"].partition(",")
    summary = (
        "Проверьте заявку:\n\n"
        f"Объект: {OBJECT_LABELS.get(data['object_type'], data['object_type'])}\n"
        f"Ремонт: {REPAIR_LABELS.get(data['repair_type'], data['repair_type'])}\n"
        f"Площадь: {data['area']} м²\n"
        f"Город: {city.strip()}\n"
        f"Адрес: {address.strip()}\n"
        f"Бюджет: {data['budget']} ₽\n"
        f"Начало: {data['start_date']}\n"
        f"Имя: {data['name']}\n"
        f"Телефон: {data['phone']}"
    )
    await message.answer(summary, reply_markup=confirmation_keyboard())


@router.callback_query(RequestForm.confirmation, F.data == "request:cancel")
async def confirm_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Заявка отменена.")
    await callback.answer()


@router.callback_query(RequestForm.confirmation, F.data == "request:back")
async def confirm_back(callback: CallbackQuery, state: FSMContext):
    await state.set_state(RequestForm.phone)
    await callback.message.edit_text("Введите номер телефона ещё раз.")
    await callback.answer()


@router.callback_query(RequestForm.confirmation, F.data == "request:confirm")
async def confirm_request(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    city, _, address = data["location"].partition(",")

    async with AsyncSessionLocal() as session:
        user_service = UserService(session)
        user = await user_service.get_or_create_user(
            telegram_id=callback.from_user.id,
            username=callback.from_user.username,
            name=data["name"],
            phone=data["phone"],
        )

        request_service = RequestService(session)
        request = await request_service.create_request(
            user_id=user.id,
            object_type=data["object_type"],
            repair_type=data["repair_type"],
            area=Decimal(data["area"]),
            city=city.strip(),
            address=address.strip() or city.strip(),
            budget=Decimal(data["budget"]),
            desired_start_date=date.fromisoformat(data["start_date"]),
        )

        sheets = GoogleSheetsService(settings.google_credentials_dict, settings.google_sheet_id)
        try:
            await sheets.append_request(request, user)
        except Exception:
            logger.exception("Google Sheets sync failed for request %s", request.id)

        notifier = NotificationService(callback.bot)
        text = (
            f"Новая заявка #{request.id}\n"
            f"{request.city}, {request.address}\n"
            f"{request.object_type} / {request.repair_type}\n"
            f"{request.area} м², бюджет {request.budget} ₽"
        )
        await notifier.notify_managers(settings.manager_telegram_ids, text)

    await state.clear()
    await callback.message.edit_text(
        f"Заявка создана.\nНомер вашей заявки: #{request.id}"
    )
    await callback.answer()


@router.message(Command("my_requests"))
@router.message(F.text == "Мои заявки")
async def my_requests(message: Message):
    async with AsyncSessionLocal() as session:
        user_service = UserService(session)
        user = await user_service.get_or_create_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
        )
        service = RequestService(session)
        requests = await service.get_user_requests(user.id)

    if not requests:
        await message.answer("У вас пока нет заявок.")
        return

    lines = [
        f"#{item.id} — {item.status} — {item.city}, {item.address}"
        for item in requests
    ]
    await message.answer("\n".join(lines))
