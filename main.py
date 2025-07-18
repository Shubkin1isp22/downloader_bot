
from telebot import TeleBot, apihelper
import os, yt_dlp, re, glob, time
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
    text = "Введите ссылку: "
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
    quality = None

    bot.edit_message_text("Вы нажали на кнопку Лучшее качество\nОжидаем начала скачивания⌛.",chat_id = chat_id, message_id = message_id)
    download(url, format, chat_id, message_id, user_id, quality)

@bot.callback_query_handler(func=lambda call : call.data == "full")
def full_hd_quality(call):
    bot.answer_callback_query(call.id)

    chat_id = call.message.chat.id
    user_id = call.from_user.id
    message_id = call.message.id
    format = 'bestvideo[vscodec^=avc1][height=1080] + bestaudio[vscodec^=mp4a]'
    url = users_urls.get(user_id)
    quality = 1080

    bot.edit_message_text("Вы нажали на кнопку 1080p\nОжидаем начала скачивания⌛.", chat_id=chat_id, message_id=message_id)
    download(url, format, chat_id, message_id, user_id, quality)

@bot.callback_query_handler(func=lambda call : call.data == "hd")
def hd_quality(call):
    bot.answer_callback_query(call.id)

    chat_id = call.message.chat.id
    user_id = call.from_user.id
    message_id = call.message.id
    format = 'bestvideo[vscodec^=avc1][height=720] + bestaudio[vscodec^=mp4a]'
    url = users_urls.get(user_id)
    quality = 720

    bot.edit_message_text("Вы нажали на кнопку 720p\nОжидаем начала скачивания⌛.", chat_id=chat_id, message_id=message_id)
    download(url, format, chat_id, message_id, user_id, quality)

@bot.callback_query_handler(func=lambda call : call.data == "phone")
def bad_quality(call):
    bot.answer_callback_query(call.id)

    chat_id = call.message.chat.id
    user_id = call.from_user.id
    print(user_id)
    message_id = call.message.id
    format = 'bestvideo[vscodec^=avc1][height=480] + bestaudio[vscodec^=mp4a]'
    url = users_urls.get(user_id)
    quality = 480

    bot.edit_message_text("Вы нажали на кнопку 480p\nОжидаем начала скачивания⌛.", chat_id=chat_id, message_id=message_id)
    download(url, format, chat_id, message_id, user_id, quality)




def download(url, format, chat_id, message_id, user_id, quality):

    user_path = os.path.join("downloads", str(user_id))
    os.makedirs(user_path, exist_ok=True)
    hook = my_hook(chat_id, message_id)

    options = {
        'format': f'{format}/best',
        'noplaylist': True,
        'outtmpl': f'{user_path}/%(title)s.%(ext)s',
        'cookiesfrombrowser': ("chrome",),
        'merge_output_format':'mp4',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',  # используем ffmpeg для перекодировки
            'preferedformat': 'mp4' # конвертируем в формат mp4
        }],
        'progress_hooks':[hook]
    }
    try:
        with YoutubeDL(options) as ytdl:
            info = ytdl.extract_info(url, download=False)
            filesize = info.get('filesize') or 0
            maybe_filesize = info.get('filesize_approx')
            videosize, audiosize = 0, 0
            formats = info.get('formats', [])
            if quality:
                for f in formats:
                    if f.get('vcodec', '').startswith('avc1') and f.get('height') == quality:
                        videosize = f.get('filesize') or 0
                    if f.get('acodec', '').startswith('mp4a'):
                        audiosize = f.get('filesize') or 0
                total_size = videosize + audiosize
                if not total_size:
                    total_size = filesize or maybe_filesize or 0
            else:
                for f in formats:
                    if f.get('vcodec', '').startswith('avc1'):
                        videosize = max(videosize, f.get('filesize') or 0)
                    if f.get('acodec', '').startswith('mp4a'):
                        audiosize = max(audiosize, f.get('filesize') or 0)
                total_size = audiosize + videosize
            if total_size and isinstance(total_size, (int, float)) and (total_size / (1024 * 1024) > 50):
                print("Парсинг стработал!")
                bot.edit_message_text("Это видео больше 50mb!\nА telegram не позволяет ботам передвать такие файлы", chat_id=chat_id, message_id=message_id)
                return
            
    except Exception as e:
        print(f"Во время парсинга данных произошла ошибка: ",{e})
    
    
    try:
        with YoutubeDL(options) as ydl:
            ydl.download([url])
            
    except Exception as e:
        print("Видео не скачалось на сервер, ошибка типа: ", e)
        bot.send_message(chat_id,f"Скачать не удалось, попробуйте ещё раз.")

    all_video_of_user = glob.glob(f"downloads/{user_id}/*")
    if not all_video_of_user:
        bot.edit_message_text("скачать не удалось((", chat_id=chat_id, message_id=message_id)
        return
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
            return
    os.remove(last_video_of_user)
    bot.delete_message(chat_id, message_id)

def my_hook(chat_id, message_id):
    last_time = 0
    def new_hook(logs0):
        size = logs0.get('downloaded_bytes') / (1024 * 1024)
        status = logs0.get('status', 'Unknown')
        total = logs0.get('total_bytes') or 0
        downloaded_now = logs0.get('downloaded_bytes') or 0
        if total > 0:
            percent = downloaded_now / total * 100
            text = f"Размер файла: {size:.2f}MB\nПроцент загрузки: {percent:.1f}%"
        else:
            text = f"Размер файла: {size:.2f}MB\nПроцент загрузки: Неизвестен"
        now_time = time.time()
        nonlocal last_time
    
        if status == 'downloading':
            if now_time-last_time > 1:
                try:
                    bot.edit_message_text(text, chat_id=chat_id, message_id=message_id)
                    last_time = now_time
                except Exception as e:
                    last_time = now_time
                    if "message is not modified" not in str(e):
                        raise e
        else:
            bot.edit_message_text("Видео скачано и отправляется с сервера", chat_id=chat_id, message_id=message_id)
    return new_hook



print("Бот в работе...")
bot.polling(non_stop=True, timeout=100)