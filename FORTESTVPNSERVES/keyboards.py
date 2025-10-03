from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import SUPPORT_USERNAME

def get_main_menu():
    """Создание главного меню с инлайн-кнопками."""
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("✅Получить конфиг✅", callback_data="get_config"),
        InlineKeyboardButton("📄Инструкция📄", url="https://t.me/instructionforvpn/2"),
        InlineKeyboardButton("↗️О преимуществах↗️", callback_data="plus"),
        InlineKeyboardButton("✊О планах✊", callback_data="future_plans"),
        InlineKeyboardButton("☎️Техподдержка☎️", url=f"https://t.me/{SUPPORT_USERNAME[1:]}")
    )
    return keyboard

def get_admin_panel():
    """Создание клавиатуры админ-панели."""
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("БД пользователей", callback_data="view_users"),
        InlineKeyboardButton("Выкачать БД", callback_data="download_db"),
        InlineKeyboardButton("Изменить конфиг", callback_data="set_config"),
        InlineKeyboardButton("Отправить рассылку", callback_data="broadcast") 
    )
    return keyboard

def get_agreement_keyboard():
    """Создание клавиатуры для соглашения."""
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("☑️Я соглашаюсь☑️", callback_data="agree"))
    return keyboard

def get_broadcast_keyboard(url=None):
    """Создание клавиатуры для рассылки с опциональной ссылкой и кнопкой удаления."""
    keyboard = InlineKeyboardMarkup()
    if url:
        keyboard.add(InlineKeyboardButton("♻️Перейти♻️", url=url))
    keyboard.add(InlineKeyboardButton("❌Удалить сообщение❌", callback_data="delete_broadcast"))

    return keyboard
