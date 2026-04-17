import os
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

def quality_menu(url):
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("🎵 128 kbps", callback_data=f"128|{url}"),
        InlineKeyboardButton("🔥 320 kbps", callback_data=f"320|{url}")
    )
    return kb

@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    await msg.answer("🎧 Отправь ссылку и выбери качество")

@dp.message_handler()
async def handle_message(message: types.Message):
    url = message.text.strip()

    if not url.startswith("http"):
        await message.reply("❌ Пришли корректную ссылку")
        return

    await message.reply("🎚 Выбери качество:", reply_markup=quality_menu(url))

@dp.callback_query_handler()
async def process_callback(callback: types.CallbackQuery):
    quality, url = callback.data.split("|")

    msg = await callback.message.edit_text("⏳ Обрабатываю...")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'audio.%(ext)s',
        'noplaylist': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': quality,
        }],
    }

    try:
        await msg.edit_text("📥 Скачиваю...")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title", "audio")

        await msg.edit_text("📤 Отправляю...")

        filename = "audio.mp3"

        with open(filename, "rb") as audio:
            await bot.send_audio(callback.from_user.id, audio, title=title)

        os.remove(filename)

        await msg.edit_text("✅ Готово!")

    except Exception:
        await bot.send_message(callback.from_user.id, "❌ Ошибка")

if __name__ == "__main__":
    executor.start_polling(dp)
