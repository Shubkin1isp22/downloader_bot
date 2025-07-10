import glob

from telebot import TeleBot
import os, yt_dlp
from yt_dlp import YoutubeDL
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("TOKEN")

bot = TeleBot(token)

@bot.message_handler(commands=["start", "help"])
def start(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    text = "Приветствую вас!\nЭто бот для скачивания видео по ссылке\nВам достаточно вставить ссылку\nи бот начнёт скачивание\nА когда скачает - тут же отправит вам!"
    bot.send_message(chat_id, text)

@bot.message_handler(commands=["download"])
def download_0(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    bot.send_message(chat_id, "Введите ссылку: ")
    bot.register_next_step_handler(message, download)
def download(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    url = message.text

    user_path = os.path.join("downloads", str(user_id))
    os.makedirs(user_path, exist_ok=True)

    options = {
        'format': 'bestvideo[vcodec^=avc1][ext=mp4]+bestaudio[acodec^=mp4a][ext=m4a]/best[ext=mp4]/best',
        'noplaylist': True,
        'outtmpl': f'{user_path}/%(title)s.%(ext)s',
        'cookiesfrombrowser': ("chrome",),
        'merge_output_format':'mp4',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',  # используем ffmpeg для перекодировки
            'preferedformat': 'mp4' # конвертируем в формат mp4
        }]
    }
    with YoutubeDL(options) as ydl:
        ydl.download([url])

    all_video_of_user = glob.glob(f"downloads/{user_id}/*")
    last_video_of_user = max(all_video_of_user, key=os.path.getctime)
    with open(last_video_of_user, "rb") as video:
        bot.send_document(chat_id, video)





print("Бот в работе...")
bot.polling()