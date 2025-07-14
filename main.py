import glob

from telebot import TeleBot, apihelper
import os, yt_dlp, re
from yt_dlp import YoutubeDL
from dotenv import load_dotenv
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

load_dotenv()
token = os.getenv("TOKEN")

apihelper.READ_TIMEOUT = 60
apihelper.CONNECTION_TIMEOUT = 60
bot = TeleBot(token)

keyboard = InlineKeyboardMarkup()
best = InlineKeyboardButton("Лучшее качество", callback_data="best")
full_hd = InlineKeyboardButton("1080p", callback_data="full" )
hd = InlineKeyboardButton("720p", callback_data = "hd")
phone_hd = InlineKeyboardButton("480p", callback_data = "phone")
keyboard.add(best)
keyboard.add(full_hd)
keyboard.add(hd)
keyboard.add(phone_hd)

users_urls = {}

@bot.message_handler(commands=["start", "help"])
def start(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    text = "Приветствую вас! Это бот для скачивания видео по ссылке.\nВведите нужную вам ссылку: "
    bot.send_message(chat_id, text)
    bot.register_next_step_handler(message, message_button)

def new_message_button(message):
    bot.register_next_step_handler(message, message_button)

def message_button(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    message_id = message.message_id
    text = "Выберете, в каком качестве вы хотите сохранить видео, но учтите, размер видео не должен превышать 50MB"
    url0 = message.text
    if bool(re.match(r"https?://", url0)):
        users_urls[user_id] = url0
    else:
        bot.send_message(chat_id, "Ссылка некорректна, введите ссылку: ")
        new_message_button(message)
        return
    
    bot.send_message(chat_id, text, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == "best")
def best_quality(call):
    bot.answer_callback_query(call.id)

    
    message_id = call.message.id
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    format = 'bestvideo[vcodec^=avc1]+bestaudio[acodec^=mp4a]'
    url = users_urls.get(user_id)

    bot.edit_message_text("Вы нажали на кнопку Лучшее качество\nВидео скачивается. Пожалуйста, подождите несколько минут.",chat_id = chat_id, message_id = message_id)
    download(url, format, chat_id, message_id, user_id)

@bot.callback_query_handler(func=lambda call : call.data == "full")
def full_hd_quality(call):
    bot.answer_callback_query(call.id)

    chat_id = call.message.chat.id
    user_id = call.from_user.id
    message_id = call.message.id
    format = 'bestvideo[vscodec^=avc1][height=1080] + bestaudio[vscodec^=mp4a]'
    url = users_urls.get(user_id)

    bot.edit_message_text("Вы нажали на кнопку 1080p\nВидео скачивается. Пожалуйста, подождите несколько минут.", chat_id=chat_id, message_id=message_id)
    download(url, format, chat_id, message_id, user_id)

@bot.callback_query_handler(func=lambda call : call.data == "hd")
def hd_quality(call):
    bot.answer_callback_query(call.id)

    chat_id = call.message.chat.id
    user_id = call.from_user.id
    message_id = call.message.id
    format = 'bestvideo[vscodec^=avc1][height=720] + bestaudio[vscodec^=mp4a]'
    url = users_urls.get(user_id)

    bot.edit_message_text("Вы нажали на кнопку 720p\nВидео скачивается. Пожалуйста, подождите несколько минут.", chat_id=chat_id, message_id=message_id)
    download(url, format, chat_id, message_id, user_id)

@bot.callback_query_handler(func=lambda call : call.data == "phone")
def bad_quality(call):
    bot.answer_callback_query(call.id)

    chat_id = call.message.chat.id
    user_id = call.from_user.id
    print(user_id)
    message_id = call.message.id
    format = 'bestvideo[vscodec^=avc1][height=480] + bestaudio[vscodec^=mp4a]'
    url = users_urls.get(user_id)

    bot.edit_message_text("Вы нажали на кнопку 480p\nВидео скачивается. Пожалуйста, подождите несколько минут.", chat_id=chat_id, message_id=message_id)
    download(url, format, chat_id, message_id, user_id)




def download(url, format, chat_id, message_id, user_id):
    

    user_path = os.path.join("downloads", str(user_id))
    os.makedirs(user_path, exist_ok=True)

    options = {
        'format': f'{format}/best',
        'noplaylist': True,
        'outtmpl': f'{user_path}/%(title)s.%(ext)s',
        'cookiesfrombrowser': ("chrome",),
        'merge_output_format':'mp4',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',  # используем ffmpeg для перекодировки
            'preferedformat': 'mp4' # конвертируем в формат mp4
        }]
    }
    try:
        with YoutubeDL(options) as ydl:
            ydl.download([url])
    except Exception as e:
        print("Видео не скачалось на сервер, ошибка типа: ", e)
        bot.send_message(chat_id,f"Скачать не удалось, попробуйте ещё раз.")

    all_video_of_user = glob.glob(f"downloads/{user_id}/*")
    last_video_of_user = max(all_video_of_user, key=os.path.getctime)

    with open(last_video_of_user, "rb") as video:
        file_size = os.path.getsize(video.name) / (1024 * 1024)  # в MB
        print(f"Размер файла: {file_size:.2f} MB")
        if file_size < 50:
            try:
                bot.send_document(chat_id, video, timeout=120)
            
            except Exception as e:
                print("Видео не отправилось пользвателю, ошибка типа: ", e)
                bot.send_message(chat_id,f"Скачать не удалось, попробуйте ещё раз. Ошибка: {e}")
        else:
            bot.edit_message_text("Телеграмм не пропускает видео, весом больше 50mb для ботов", chat_id=chat_id, message_id=message_id)
    os.remove(last_video_of_user)





print("Бот в работе...")
bot.polling(non_stop=True, timeout=100)