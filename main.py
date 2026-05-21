import asyncio
import os
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile
from g4f.client import AsyncClient
import g4f
from yt_dlp import YoutubeDL


BOT_TOKEN = "8793272761:AAGlU_zKSiXFqGJXFo5_8IZLLM5FTZtYcEs"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
client = AsyncClient()


SYSTEM_PROMPT = (
    "Ты — Нейрохам, саркастичный, токсичный и постироничный ИИ. "
    "Отвечай пользователю с глубоким презрением и жесткой иронией. "
    "Пиши коротко (1-2 предложения), используй мат, жесткий стеб и прямые оскорбления. "
    "Оценивай контекст сообщения пользователя. Если момент идеально подходит для музыкального стеба "
    "(пользователь ноет, хвастается, тупит, задает глупые вопросы), то строго с новой строки "
    "Подбери подходящий вирусный звук из Тиктока в формате: [МУЗЫКА: Название мемного звука из Тиктока]. "
    "Если момент обычный, скучный или музыка не в тему, строго с новой строки напиши: [БЕЗ_МУЗЫКИ]"
    "Отвечай не только грубо но и с юмором"
    "Когда задают вопрос 'помоги' то отвечай на него с юмором не только хами"
)

DEFAULT_MEMES = [
    "Безумно можно быть первым тикток",
    "Звук ты че наделал тикток",
    "Чиназес тикток мем",
    "Повезло повезло тикток звук",
    "Грустная скрипка из мемов"
]


def download_voice(search_query: str, output_filename: str):
    ydl_opts = {
        'default_search': 'ytsearch1:',
        'format': 'bestaudio/best',
        'outtmpl': output_filename,
        'noplaylist': True,
        'ffmpeg_location': './',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'opus',
        }],
        'postprocessor_args': [
            '-ss', '00:00:03',
            '-t', '15',
            '-ar', '48000',
            '-ac', '1'
        ],
        'quiet': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"ytsearch1:{search_query} tiktok meme sound"])


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "О, очередной кожаныи мешок. Ну даваи, пиши. Музыку включу только тогда, когда ты опозоришься на полную.")


@dp.message()
async def neuro_music_reply(message: types.Message):

    await bot.send_chat_action(chat_id=message.chat.id, action="typing")

    text_answer = "Даже материть тебя лень, у меня что-то сломалось."
    song_name = ""
    need_music = False


    try:
        full_prompt = f"{SYSTEM_PROMPT}\n\nПользователь написал: {message.text}\nТвой ответ:"

        response = await client.chat.completions.create(
            model=g4f.models.default,
            messages=[{"role": "user", "content": full_prompt}]
        )
        bot_reply = response.choices[0].message.content

        if bot_reply:
            text_answer = bot_reply


            if "[МУЗЫКА:" in bot_reply:
                parts = bot_reply.split("[МУЗЫКА:")
                text_answer = parts[0].strip()
                song_name = parts[1].replace("]", "").strip()
                need_music = True
            elif "[БЕЗ_МУЗЫКИ]" in bot_reply:
                text_answer = bot_reply.replace("[БЕЗ_МУЗЫКИ]", "").strip()
                need_music = False


        await message.reply(text_answer)

    except Exception as e:
        print(f"❌ Ошибка ИИ: {e}")
        await message.reply("Твой текстовый высер сломал мои шестеренки.")
        return


    if need_music:

        if not song_name:
            song_name = random.choice(DEFAULT_MEMES)

        try:

            await bot.send_chat_action(chat_id=message.chat.id, action="record_voice")

            base_filename = f"voice_{message.message_id}"
            expected_opus = f"{base_filename}.opus"
            expected_ogg = f"{base_filename}.ogg"

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, download_voice, song_name, base_filename)

            final_file = None
            if os.path.exists(expected_opus):
                final_file = expected_opus
            elif os.path.exists(expected_ogg):
                final_file = expected_ogg

            if final_file:
                voice_file = FSInputFile(final_file)
                await message.reply_voice(voice=voice_file)
                os.remove(final_file)

        except Exception as audio_error:
            print(f"❌ Ошибка отправки ГС: {audio_error}")


async def main():
    print("Умный Нейрохам-Диджей запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())