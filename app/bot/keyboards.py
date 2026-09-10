from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Новая заявка")],
            [KeyboardButton(text="Мои заявки"), KeyboardButton(text="Помощь")],
        ],
        resize_keyboard=True,
    )


def cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Отмена")]],
        resize_keyboard=True,
    )


def confirmation_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Подтвердить", callback_data="request:confirm")
    builder.button(text="Назад", callback_data="request:back")
    builder.button(text="Отменить", callback_data="request:cancel")
    builder.adjust(1)
    return builder.as_markup()


def object_keyboard():
    builder = InlineKeyboardBuilder()
    for value, label in [
        ("apartment", "Вся квартира"),
        ("kitchen", "Кухня"),
        ("bathroom", "Ванная"),
        ("room", "Комната"),
        ("other", "Другое"),
    ]:
        builder.button(text=label, callback_data=f"object:{value}")
    builder.adjust(2)
    return builder.as_markup()


def repair_keyboard():
    builder = InlineKeyboardBuilder()
    for value, label in [
        ("cosmetic", "Косметический"),
        ("capital", "Капитальный"),
        ("designer", "Дизайнерский"),
        ("undecided", "Не определился"),
    ]:
        builder.button(text=label, callback_data=f"repair:{value}")
    builder.adjust(2)
    return builder.as_markup()
