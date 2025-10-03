import logging
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from config import ADMIN_IDS, AGREEMENT_TEXT
from database import get_user_internal_id, register_user, update_config, get_user_stats, get_all_user_ids, get_current_config
from keyboards import get_main_menu, get_admin_panel, get_agreement_keyboard, get_broadcast_keyboard
from states import UserState

def is_admin(user_id):
    """Проверка, является ли пользователь админом."""
    return user_id in ADMIN_IDS

def register_handlers(dp: Dispatcher):
    """Регистрация всех обработчиков."""

    @dp.message_handler(commands=['cancel'], state='*')
    async def cancel_command(message: types.Message, state: FSMContext):
        await state.finish()
        await message.answer("Действие отменено. Используйте /start или /admin для продолжения.")

    @dp.message_handler(commands=['start'], state='*')
    async def start_command(message: types.Message, state: FSMContext):
        await state.finish()
        user_id = message.from_user.id
        username = message.from_user.username or "NoUsername"

        internal_id = get_user_internal_id(user_id)
        if internal_id:
            main_menu_message = await message.answer(
                f"Вы зарегистрированы!\nВаш ID-VPN: {internal_id}",
                reply_markup=get_main_menu()
            )
            await state.set_state(UserState.MainMenu)
            await state.update_data(main_menu_message_id=main_menu_message.message_id)
        else:
            await message.answer(AGREEMENT_TEXT, reply_markup=get_agreement_keyboard())
            await UserState.AwaitingAgreement.set()

    @dp.callback_query_handler(text="agree", state=UserState.AwaitingAgreement)
    async def process_agreement(callback_query: types.CallbackQuery, state: FSMContext):
        user_id = callback_query.from_user.id
        username = callback_query.from_user.username or "NoUsername"

        internal_id, config = register_user(user_id, username)
        if internal_id is None or config is None:
            await callback_query.message.answer("Ошибка при генерации конфига. Попробуйте позже.")
            return

        try:
            await callback_query.message.bot.delete_message(
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id
            )
        except Exception as e:
            logging.warning(f"Не удалось удалить сообщение с соглашением: {e}")

        main_menu_message = await callback_query.message.answer(
            f"Регистрация успешна!\nВаш ID-VPN: {internal_id}",
            reply_markup=get_main_menu()
        )
        await state.set_state(UserState.MainMenu)
        await state.update_data(main_menu_message_id=main_menu_message.message_id)
        await callback_query.answer()

    @dp.callback_query_handler(text="get_config", state=UserState.MainMenu)
    async def get_config(callback_query: types.CallbackQuery):
        user_id = callback_query.from_user.id
        internal_id = get_user_internal_id(user_id)

        if internal_id:
            config_text = get_current_config()
            if config_text is None:
                await callback_query.message.answer("Ошибка: конфиг недоступен. Обратитесь к администратору.")
                return
            await callback_query.message.answer(f"Ваш ID-VPN: {internal_id}\nКонфиг: {config_text}")
        else:
            await callback_query.message.answer("Вы не зарегистрированы. Используйте /start для регистрации.")

        await callback_query.answer()

    @dp.callback_query_handler(text="future_plans", state=UserState.MainMenu)
    async def show_plans(callback_query: types.CallbackQuery, state: FSMContext):
        user_data = await state.get_data()
        main_menu_message_id = user_data.get("main_menu_message_id")

        try:
            await callback_query.message.bot.edit_message_text(
                text="<b>Мы держим курс в разработке быстрого и надёжного ВПН в условиях замедления и ограничений в РФ</b>, cтримясь создать конфигурации под все возможные сценарии для всех уровней пользователей, придерживаясь принципа простоты, удобства, доступа для всех желающих!\n\n"
                     "В некотором роде, это только MVP-версия для анализа поведения и спроса потребителя. <b>Если вы заинтересованы в сотрудничестве или работе в дальнейшем: @Crypto44LDN</b>\n"
                     "P.S.\n"
                     "<blockquote><span class='tg-spoiler'>Мы помним о содержании статей УК РФ Ст. 272: «Неправомерный доступ к компьютерной информаци», Ст. 273: «Создание, использование и распространение вредоносных компьютерных программ», Ст. 274: «Нарушение правил эксплуатации средств хранения/передачи компьютерной информации», Ст. 63, Ст. 274.4 и 274.5 (от 2025 г.) и можем сказать, что не поддерживаем и не занимаемся противозаконной или преступной деятельностью. При заявлении соответствующих служб РФ в соответствии с ФЗ-374 (\"Закон Яровой\"), ФЗ-149 (\"Об информации\"), ФЗ-152 (\"О персональных данных\") мы готовы сотрудничать.\n\n"
                     "Все вопросы также: @Episthema</span></blockquote>",
                parse_mode='HTML',
                chat_id=callback_query.message.chat.id,
                message_id=main_menu_message_id,
                reply_markup=get_main_menu()
            )
        except Exception as e:
            logging.error(f"Ошибка редактирования сообщения: {e}")

        await callback_query.answer()

    @dp.callback_query_handler(text="plus", state=UserState.MainMenu)
    async def show_plus_vpn(callback_query: types.CallbackQuery, state: FSMContext):
        user_data = await state.get_data()
        main_menu_message_id = user_data.get("main_menu_message_id")
        try:
            await callback_query.message.bot.edit_message_text(
                text="❗️В условиях 2025-ого года, интернет по всей России был замедлен. Это связано не только с угрозой территориальной безопасности, но и с тестированием «Белых списков РФ». Многие операторы выдают низкую скорость интернета, небольшая часть осталась рабочей. <b>И это уже не сон и не слух, а реальность...</b>\n"
                     "🤝<b>Но наша команда нашла способ, как попасть в интернет.</b> 📑С новейшим протоколом XRay и шифрованием под VK это мтало возможным! А проще говоря:\n"
                     "<b>✊С нашим ВПНом вам не страшны замедления и блокировки даже с мобильным интернетом. Вы можете не бояться о том, что ваши логи прозрачны и данные утекают.</b>\n\n"
                     "<b>✅С НАМИ ВЫ ВСЕГДА В БЕЗОПАСНОСТИ И ВСЕГДА В СЕТИ!</b>\n\n"
                     "<span class='tg-spoiler'><b>Кроме того, если ваш оператор сотовой связи предоставляет вам безлимит на ВК, то любой трафик через наш ВПН будет предоставлять вам безлимит.</b></span>",
                parse_mode='HTML',
                chat_id=callback_query.message.chat.id,
                message_id=main_menu_message_id,
                reply_markup=get_main_menu()
            )
        except Exception as e:
            logging.error(f"Ошибка редактирования сообщения: {e}")

        await callback_query.answer()

    @dp.message_handler(commands=['admin'], state='*')
    async def admin_panel(message: types.Message, state: FSMContext):
        await state.finish()
        user_id = message.from_user.id
        if not is_admin(user_id):
            await message.answer("У вас нет доступа к админ-панели.")
            return

        await message.answer("Админ-панель:", reply_markup=get_admin_panel())

    @dp.callback_query_handler(text="view_users")
    async def view_users(callback_query: types.CallbackQuery):
        user_id = callback_query.from_user.id
        if not is_admin(user_id):
            await callback_query.message.answer("У вас нет доступа.")
            return

        stats = get_user_stats()
        if stats is None:
            await callback_query.message.answer("Ошибка базы данных. Попробуйте позже.")
            return

        response = (
            f"Статистика пользователей:\n"
            f"Общее количество: {stats['total']}\n"
            f"Новых за 24 часа: {stats['24h']}\n"
            f"Новых за 3 дня: {stats['3d']}\n"
            f"Новых за неделю: {stats['7d']}\n"
            f"Новых за месяц: {stats['30d']}"
        )
        await callback_query.message.answer(response)
        await callback_query.answer()

    @dp.callback_query_handler(text="download_db")
    async def download_db(callback_query: types.CallbackQuery):
        user_id = callback_query.from_user.id
        if not is_admin(user_id):
            await callback_query.message.answer("У вас нет доступа.")
            return

        users = get_all_users()  # Предполагаем, что функция возвращает список словарей: [{'tg_id': int, 'vpn_id': str, 'username': str, 'registered_at': datetime}, ...]
        if users is None:
            await callback_query.message.answer("Ошибка базы данных. Попробуйте позже.")
            return

        # Создаем CSV в памяти
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['TG ID', 'VPN ID', 'Username', 'Registered At'])  # Заголовки

        for user in users:
            writer.writerow([user['tg_id'], user['vpn_id'], user['username'], user['registered_at']])

        output.seek(0)
        file = types.InputFile(output, filename="users_db.csv")

        await callback_query.message.bot.send_document(
            chat_id=callback_query.message.chat.id,
            document=file,
            caption="Выкачанная база данных пользователей (CSV)"
        )
        await callback_query.answer()

    @dp.callback_query_handler(text="set_config")
    async def set_config_prompt(callback_query: types.CallbackQuery, state: FSMContext):
        user_id = callback_query.from_user.id
        if not is_admin(user_id):
            await callback_query.message.answer("У вас нет доступа.")
            return

        await callback_query.message.answer("Введите новый конфиг:")
        await state.set_state(UserState.AwaitingNewConfig)
        await callback_query.answer()

    @dp.message_handler(state=UserState.AwaitingNewConfig)
    async def process_new_config(message: types.Message, state: FSMContext):
        user_id = message.from_user.id
        if not is_admin(user_id):
            await message.answer("У вас нет доступа.")
            await state.finish()
            return

        new_config = message.text
        if update_config(new_config):
            await message.answer(f"Конфиг обновлен: {new_config}")
            logging.info(f"Админ {user_id} обновил конфиг на: {new_config}")
        else:
            await message.answer("Ошибка базы данных. Попробуйте позже.")

        await state.finish()

    @dp.callback_query_handler(text="broadcast")
    async def broadcast_prompt(callback_query: types.CallbackQuery, state: FSMContext):
        user_id = callback_query.from_user.id
        if not is_admin(user_id):
            await callback_query.message.answer("У вас нет доступа.")
            return

        await callback_query.message.answer("Введите текст рассылки:")
        await state.set_state(UserState.AwaitingBroadcastText)
        await callback_query.answer()

    @dp.message_handler(state=UserState.AwaitingBroadcastText)
    async def process_broadcast_text(message: types.Message, state: FSMContext):
        user_id = message.from_user.id
        if not is_admin(user_id):
            await message.answer("У вас нет доступа.")
            await state.finish()
            return

        await state.update_data(broadcast_text=message.text)
        await message.answer("Отправьте изображение для рассылки или введите /skip, чтобы пропустить:")
        await state.set_state(UserState.AwaitingBroadcastPhoto)

    @dp.message_handler(content_types=['photo'], state=UserState.AwaitingBroadcastPhoto)
    async def process_broadcast_photo(message: types.Message, state: FSMContext):
        user_id = message.from_user.id
        if not is_admin(user_id):
            await message.answer("У вас нет доступа.")
            await state.finish()
            return

        photo = message.photo[-1].file_id
        await state.update_data(broadcast_photo=photo)
        await message.answer("Введите URL для кнопки или /skip, чтобы пропустить:")
        await state.set_state(UserState.AwaitingBroadcastUrl)

    @dp.message_handler(commands=['skip'], state=UserState.AwaitingBroadcastPhoto)
    async def skip_broadcast_photo(message: types.Message, state: FSMContext):
        user_id = message.from_user.id
        if not is_admin(user_id):
            await message.answer("У вас нет доступа.")
            await state.finish()
            return

        await state.update_data(broadcast_photo=None)
        await message.answer("Введите URL для кнопки или /skip, чтобы пропустить:")
        await state.set_state(UserState.AwaitingBroadcastUrl)

    @dp.message_handler(state=UserState.AwaitingBroadcastUrl)
    async def process_broadcast_url(message: types.Message, state: FSMContext):
        user_id = message.from_user.id
        if not is_admin(user_id):
            await message.answer("У вас нет доступа.")
            await state.finish()
            return

        url = message.text if message.text != "/skip" else None
        await state.update_data(broadcast_url=url)
        await send_broadcast(message, state)

    @dp.message_handler(commands=['skip'], state=UserState.AwaitingBroadcastUrl)
    async def skip_broadcast_url(message: types.Message, state: FSMContext):
        user_id = message.from_user.id
        if not is_admin(user_id):
            await message.answer("У вас нет доступа.")
            await state.finish()
            return

        await state.update_data(broadcast_url=None)
        await send_broadcast(message, state)

    async def send_broadcast(message: types.Message, state: FSMContext):
        user_data = await state.get_data()
        broadcast_text = user_data.get("broadcast_text")
        broadcast_photo = user_data.get("broadcast_photo")
        broadcast_url = user_data.get("broadcast_url")

        user_ids = get_all_user_ids()
        sent_count = 0
        for user_id in user_ids:
            try:
                keyboard = get_broadcast_keyboard(broadcast_url)
                if broadcast_photo:
                    await message.bot.send_photo(
                        chat_id=user_id,
                        photo=broadcast_photo,
                        caption=broadcast_text,
                        reply_markup=keyboard
                    )
                else:
                    await message.bot.send_message(
                        chat_id=user_id,
                        text=broadcast_text,
                        reply_markup=keyboard
                    )
                sent_count += 1
            except Exception as e:
                logging.error(f"Ошибка отправки сообщения пользователю {user_id}: {e}")

        await message.answer(f"Рассылка завершена. Отправлено {sent_count} сообщений.")
        await state.finish()

    @dp.callback_query_handler(text="delete_broadcast")
    async def delete_broadcast_message(callback_query: types.CallbackQuery):
        try:
            await callback_query.message.bot.delete_message(
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id
            )
            await callback_query.answer("Сообщение удалено.")
        except Exception as e:
            logging.error(f"Ошибка удаления сообщения: {e}")

            await callback_query.answer("Не удалось удалить сообщение.")
