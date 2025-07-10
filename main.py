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

print("Бот в работе...")
bot.polling()