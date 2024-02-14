import telebot
import json

from SECRET import TG_KEY, ADMINS
from telebot import types
import os


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


with open("text.json") as f:
    text = json.load(f)

API_KEY = TG_KEY

bot = telebot.TeleBot(TG_KEY)


def is_admin(msg) -> bool:
    if str(msg.from_user.id) in ADMINS:
        return True
    return False


def find_path(corpus: str, aud: str) -> (str or None, bool):
    MOV = 'videos/' + 'corpus' + corpus + '/' + aud + "." + 'MOV'
    MP4 = 'videos/' + 'corpus' + corpus + '/' + aud + "." + 'mp4'
    if os.path.isfile(MOV):
        return (MOV, True)
    if os.path.isfile(MP4):
        return (MP4, True)
    return (None, False)


@bot.message_handler(commands=["start"])
def start(msg):
    bot.send_message(msg.from_user.id, text["hello"])


@bot.message_handler(commands=["path"])
def path(msg):
    bot.send_message(msg.from_user.id, "Введите номер корпуса")
    bot.register_next_step_handler(msg, set_corp)


def set_corp(msg):
    corp = msg.text
    if corp is None:
        bot.send_message(msg.from_user.id, "Введите номер аудитории")
        bot.register_next_step_handler(msg, set_corp)
        return
    bot.send_message(msg.from_user.id, "Введите номер аудитории")
    bot.register_next_step_handler(msg, find, corp=corp)


def find(msg, corp):
    aud = msg.text
    file, status = find_path(corp, aud)
    if status == False:
        bot.send_message(msg.from_user.id, "Простите но путь к этой аудитории еще не добавили")
        return
    with open(file, 'rb') as video:
        bot.send_video(msg.from_user.id, video)


@bot.message_handler(commands=["add"])
def add(msg):
    if not is_admin(msg):
        return

    bot.send_message(msg.from_user.id, "Введите номер корпуса")
    bot.register_next_step_handler(msg, get_corp)


def get_corp(msg):
    corp = msg.text
    if corp is None:
        bot.send_message(msg.from_user.id, "Введите номер аудитории")
        bot.register_next_step_handler(msg, get_corp)
        return
    bot.send_message(msg.from_user.id, "Введите номер аудитории")
    bot.register_next_step_handler(msg, get_aud, corp=corp)


def get_aud(msg, corp):
    aud = msg.text
    if aud is None:
        bot.send_message(msg.from_user.id, "Введите номер аудитории")
        bot.register_next_step_handler(msg, get_aud, corp=corp)
        return
    bot.send_message(msg.from_user.id, "Отправьте видео")
    bot.register_next_step_handler(msg, save, aud=aud, corp=corp)


def save(msg, aud, corp):
    try:
        file_info = bot.get_file(msg.video.file_id)
    except:
        bot.send_message(msg.from_user.id, "Отправьте видео")
        bot.register_next_step_handler(msg, save, aud=aud, corp=corp)
        return

    downloaded_file = bot.download_file(file_info.file_path)
    src = 'videos/' + 'corpus' + corp + '/' + aud + "." + file_info.file_path.split(".")[-1]
    with open(src, 'wb') as new_file:
        new_file.write(downloaded_file)
    bot.send_message(msg.from_user.id, f"аудитория {aud} добаленна")


def main():
    print(bcolors.OKGREEN + 'Status: ' + bcolors.BOLD + 'Working' + bcolors.BOLD + bcolors.OKGREEN)
    print(bcolors.HEADER)
    bot.polling(none_stop=True, interval=0)
    print(bcolors.WARNING + 'Status: ' + bcolors.BOLD + 'Not Working' + bcolors.BOLD + bcolors.WARNING)


if __name__ == '__main__':
    main()
