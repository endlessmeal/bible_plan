import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from bible_api import BibleAPI
from config import get_app_settings
from const import BOOK_MAPPING
from models import ReadingPlan
from users import add_user_id, get_all_user_ids

settings = get_app_settings()

# Загрузка токена из переменной окружения
BOT_TOKEN = settings.BOT_TOKEN

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

engine = create_engine(settings.SQLITE_DB_PATH)
Session = sessionmaker(bind=engine)


@dp.message(Command('start'))
async def cmd_start(message: Message):
    add_user_id(message.from_user.id)
    await message.answer('Привет! Я бот для ежедневного чтения Библии.\n\nИспользуй команду /today чтобы получить главы на сегодня.')


@dp.message(Command('today'))
async def cmd_today(message: Message) -> None:
    """Хендлер для команды today"""
    today = datetime.now(ZoneInfo('Europe/Moscow'))
    with Session() as session:
        plan = session.query(ReadingPlan).filter_by(month=today.month, day=today.day).first()
        if not plan:
            await message.answer('План на сегодня не найден.')
            return
        bible_api = BibleAPI(translation='rst')
        result_texts = await format_plan_text(plan, bible_api)
        for text in result_texts:
            if len(text) > 4096:
                for i in range(0, len(text), 4096):
                    await message.answer(text[i:i+4096], parse_mode='HTML')
            else:
                await message.answer(text, parse_mode='HTML')

async def daily_broadcast() -> None:
    today = datetime.now(ZoneInfo('Europe/Moscow'))
    with Session() as session:
        plan = session.query(ReadingPlan).filter_by(month=today.month, day=today.day).first()
        if not plan:
            return
        bible_api = BibleAPI(translation='rst')
        result_texts = await format_plan_text(plan, bible_api)
        user_ids = get_all_user_ids()
        for user_id in user_ids:
            for text in result_texts:
                if len(text) > 4096:
                    for i in range(0, len(text), 4096):
                        await bot.send_message(user_id, text[i:i+4096], parse_mode='HTML')
                else:
                    await bot.send_message(user_id, text, parse_mode='HTML')

async def format_plan_text(plan, bible_api) -> list:
    result_texts = []
    async def fetch_and_format(ref: str):
        try:
            book_short, chapters = ref.split('.')
        except ValueError:
            result_texts.append(f'Ошибка разбора: {ref}')
            return
        book_num = BOOK_MAPPING.get(book_short)
        if not book_num:
            result_texts.append(f'Неизвестная книга: {book_short}')
            return
        if '-' in chapters:
            start, end = map(int, chapters.split('-'))
            for ch in range(start, end + 1):
                data = await bible_api.get_chapter(book_num, ch)
                if data:
                    book_full = data.get('info', {}).get('book', book_short)
                    chapter_num = data.get('info', {}).get('chapter', ch)
                    verses = [(int(k), v) for k, v in data.items() if k.isdigit()]
                    verses.sort()
                    verses_text = '\n'.join([f"<b>{num}</b> {text}" for num, text in verses])
                    text = f"📖 <b>{book_full} {chapter_num}</b>\n\n{verses_text}"
                    result_texts.append(text)
                else:
                    result_texts.append(f'Не удалось получить {book_short} {ch}')
        else:
            ch = int(chapters)
            data = await bible_api.get_chapter(book_num, ch)
            if data:
                book_full = data.get('info', {}).get('book', book_short)
                chapter_num = data.get('info', {}).get('chapter', ch)
                verses = [(int(k), v) for k, v in data.items() if k.isdigit()]
                verses.sort()
                verses_text = '\n'.join([f"<b>{num}</b> {text}" for num, text in verses])
                text = f"📖 <b>{book_full} {chapter_num}</b>\n\n{verses_text}"
                result_texts.append(text)
            else:
                result_texts.append(f'Не удалось получить {book_short} {ch}')
    await fetch_and_format(plan.psalm)
    await fetch_and_format(plan.new_testament)
    await fetch_and_format(plan.old_testament)
    return result_texts

async def scheduler() -> None:
    while True:
        now = datetime.now(ZoneInfo('Europe/Moscow'))
        # 7:00 утра
        if now.hour == 7 and now.minute == 0:
            await daily_broadcast()
            await asyncio.sleep(60)  # чтобы не отправлять несколько раз за минуту
        else:
            await asyncio.sleep(30)

async def main():
    asyncio.create_task(scheduler())
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
