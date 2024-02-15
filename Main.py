import telebot
import sqlite3
import os

from SECRET import TG_KEY, ADMINS
from telebot import types


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


API_KEY = TG_KEY

bot = telebot.TeleBot(TG_KEY)


def is_admin(msg) -> bool:
    if str(msg.from_user.id) in ADMINS:
        return True
    return False


def find_path(corpus: str, aud: str) -> (str or None, bool):
    aud = aud.lower()
    MOV = 'videos/' + 'corpus' + corpus + '/' + aud + "." + 'MOV'
    MP4 = 'videos/' + 'corpus' + corpus + '/' + aud + "." + 'mp4'
    if os.path.isfile(MOV):
        return (MOV, True)
    if os.path.isfile(MP4):
        return (MP4, True)
    return (None, False)


@bot.message_handler(commands=["start"])
def start(msg):
    bot.send_message(msg.from_user.id, """Привет, студент! Добро пожаловать в чат-бот, который поможет тебе быстро и легко найти нужные аудитории и преподавателей в университете!

Просто выбери номер учебного корпуса и номер нужной аудитории или фамилию преподавателя, и бот пришлет тебе видео-инструкцию о том, как добраться туда. Начальной точкой является гардероб, так что не беспокойся – мы поможем тебе не заблудиться. Желаем успешных занятий!

Связь с администратором: https://t.me/skuYil

В данный момент бот работает в тестовом режиме, и вы сможете найти информацию о доступных аудиториях: 319,318,320
,Профком ,228,230,239,241,234,243,Музей,240,242,244,249,251 ,253,153,153а,338а,338,337,335,336,340,342,344,348,350,352,354,347,349,353,355,Гидравлика ,33,Столовая,128,127,130,132,134,131,Буфет,Библиотека.

Напиши номер аудитории, чтобы найти путь
/opt_structure - сменить корпус""")
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    r = f"SELECT CORP FROM USERS WHERE USER_ID = '{msg.from_user.id}'"
    if cur.execute(r).fetchone() is None:
        r = f"INSERT INTO USERS(USER_ID, CORP) VALUES ('{msg.from_user.id}', {2})"
        cur.execute(r)
        con.commit()
        con.close()

@bot.message_handler(commands=["up_professor"])
def g_caf(msg):
    if not is_admin(msg):
        return
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    r = f"SELECT Caf FROM Kafed"
    ol_caf = cur.execute(r).fetchall()
    f = []
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in ol_caf:
        s = i[0]
        f.append(types.KeyboardButton(text=s))
    markup.add(*f, row_width=1)
    con.close()
    bot.send_message(msg.from_user.id, text="Выберите кафедру", reply_markup=markup)
    bot.register_next_step_handler(msg, g_prof)


def g_prof(msg):
    caf = msg.text
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    r = f"SELECT Name, Kab, Corp FROM Prep WHERE Caf = '{caf}'"
    s = ""
    for name, kab, corp in cur.execute(r).fetchall():
        s += f"{name} Кабинет: {kab} Корпус: {corp}\n"
    if s == "":
        bot.send_message(msg.from_user.id, "Такую кафедру еще не добавили", reply_markup=types.ReplyKeyboardRemove())
        return
    bot.send_message(msg.from_user.id,
                     "ВЫБЕРИТЕ ПРЕПОДАВАТЕЛЯ ИЗ СПИСКА И НАПИШИТЕ ЕГО ИМЯ ФАМИЛИЮ И ОТЧЕСТВО ТОЧНО ТАКЖЕ"
                     " КАК В СПИСКЕ А ПОТОМ ЧЕРЕЗ ПРОБЕЛ КАБИНЕТ И КАФЕДРУ\nПРИМЕР:(Иванов Иван Иванович 312 5)",
                     reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(msg.from_user.id, s, reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, get_name, caf=caf)


def get_name(msg, caf):
    name = " ".join(msg.text.split(" ")[:3])
    cab = msg.text.split(" ")[3]
    corp = msg.text.split(" ")[4]
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    r = f"UPDATE Prep SET Kab='{cab}', Corp='{corp}' WHERE (Caf='{caf}') AND (Name='{name}')"
    try:
        cur.execute(r)
    except:
        bot.send_message(msg.from_user.id, "Что-то пошло не так")
        return
    con.commit()
    con.close()
    s = f"Успешно обновленно:\n{caf} {name} Кабинет: {cab} Корпус: {corp}"
    bot.send_message(msg.from_user.id, s)


@bot.message_handler(commands=["opt_professor"])
def giv_caf(msg):
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    r = f"SELECT Caf FROM Kafed"
    ol_caf = cur.execute(r).fetchall()
    f = []
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in ol_caf:
        s = i[0]
        f.append(types.KeyboardButton(text=s))
    markup.add(*f, row_width=1)
    con.close()
    bot.send_message(msg.from_user.id, text="Выберите кафедру", reply_markup=markup)
    bot.register_next_step_handler(msg, give_prof)


def give_prof(msg):
    caf = msg.text
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    r = f"SELECT Name, Kab, Corp FROM Prep WHERE Caf = '{caf}'"
    s = ""
    for name, kab, corp in cur.execute(r).fetchall():
        s += f"{name} Кабинет: {kab} Корпус: {corp}\n"
    if s == "":
        bot.send_message(msg.from_user.id, "Такую кафедру еще не добавили", reply_markup=types.ReplyKeyboardRemove())
        return
    bot.send_message(msg.from_user.id, s, reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(commands=["del"])
def delet(msg):
    if not is_admin(msg):
        return
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    r = f"SELECT CORP FROM USERS WHERE USER_ID = '{msg.from_user.id}'"
    corp = cur.execute(r).fetchone()
    if corp is None:
        bot.send_message(msg.from_user.id, text="У вас не выбран корпус\n /opt_structure")
        return
    corp = corp[0]
    bot.send_message(msg.from_user.id, f"Введите аудиторию(Корпус: {corp}),\nкоторую вы хотите удалить из списка:")
    f = []
    for (dirpath, dirnames, filenames) in os.walk('videos/' + 'corpus' + str(corp)):
        f.extend(filenames)
        break
    f = [x.split('.')[0] for x in f]
    bot.send_message(msg.from_user.id, '\n'.join(f))
    bot.register_next_step_handler(msg, com, f=f, corp=corp)


def com(msg, f, corp):
    if msg.text == '/ret':
        return
    if not msg.text in f:
        bot.send_message(msg.from_user.id, text="Данная аудитория не обнаружена")
        return
    pth = 'videos/' + 'corpus' + str(corp) + '/' + msg.text + ".mp4"
    os.remove(pth)
    bot.send_message(msg.from_user.id, f"аудитория {msg.text} удалена")


@bot.message_handler(commands=['list'])
def ls(msg):
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    r = f"SELECT CORP FROM USERS WHERE USER_ID = '{msg.from_user.id}'"
    corp = cur.execute(r).fetchone()
    if corp is None:
        bot.send_message(msg.from_user.id, text="У вас не выбран корпус\n /opt_structure")
        return
    corp = corp[0]
    bot.send_message(msg.from_user.id, text=f"Аудитории корпуса {corp}")
    f = []
    for (dirpath, dirnames, filenames) in os.walk('videos/' + 'corpus' + str(corp)):
        f.extend(filenames)
        break
    bot.send_message(msg.from_user.id, '\n'.join([x.split('.')[0] for x in f]))


@bot.message_handler(commands=["opt_structure"])
def opt_structure(msg):
    markup = types.ReplyKeyboardMarkup()
    b1 = types.KeyboardButton("1")
    b2 = types.KeyboardButton("2")
    b3 = types.KeyboardButton("3")
    markup.add(b1, b2, b3)
    bot.send_message(msg.from_user.id, text="Выберите корпус", reply_markup=markup)
    bot.register_next_step_handler(msg, set_corp)


def set_corp(msg):
    if not msg.text in ["1", "2", "3"]:
        bot.send_message(msg.from_user.id, text="Выберите корпус")
        bot.register_next_step_handler(msg, set_corp)
        return
    bot.send_message(msg.from_user.id, text=f"Корпус изменён на {msg.text}", reply_markup=types.ReplyKeyboardRemove())
    con = sqlite3.connect('users.db')
    cur = con.cursor()

    r = f"SELECT CORP FROM USERS WHERE USER_ID = '{msg.from_user.id}'"
    if cur.execute(r).fetchone() is None:
        r = f"INSERT INTO USERS(USER_ID, CORP) VALUES ('{msg.from_user.id}', {msg.text})"
        cur.execute(r)
        con.commit()
        con.close()
        return

    r = (f"UPDATE USERS SET CORP={msg.text} WHERE USER_ID = '{msg.from_user.id}'")
    cur.execute(r)
    con.commit()
    con.close()


@bot.message_handler(commands=["add"])
def add(msg):
    if msg.text == "/ret":
        return
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    r = f"SELECT CORP FROM USERS WHERE USER_ID = '{msg.from_user.id}'"
    corp = cur.execute(r).fetchone()
    if corp is None:
        bot.send_message(msg.from_user.id, text="У вас не выбран корпус\n /opt_structure")
        return
    corp = corp[0]
    bot.send_message(msg.from_user.id, f"Корпус: {corp}\nВведите номер аудитории",
                     reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, get_aud, corp=corp)


def get_aud(msg, corp):
    if msg.text == "/ret":
        return
    aud = msg.text
    if aud is None:
        bot.send_message(msg.from_user.id, "Введите номер аудитории")
        bot.register_next_step_handler(msg, get_aud, corp=corp)
        return
    bot.send_message(msg.from_user.id, "Отправьте видео в формате mp4")
    bot.register_next_step_handler(msg, save, aud=aud, corp=corp)


def save(msg, aud, corp):
    if msg.text == "/ret":
        return
    try:
        file_info = bot.get_file(msg.video.file_id)
    except:
        bot.send_message(msg.from_user.id, "Отправьте видео в формате mp4")
        bot.register_next_step_handler(msg, save, aud=aud, corp=corp)
        return

    downloaded_file = bot.download_file(file_info.file_path)
    if file_info.file_path.split(".")[-1] != 'mp4':
        bot.send_message(msg.from_user.id, "Отправьте видео в формате mp4")
        bot.register_next_step_handler(msg, save, aud=aud, corp=corp)
        return
    src = 'videos/' + 'corpus' + str(corp) + '/' + aud + "." + file_info.file_path.split(".")[-1]
    with open(src, 'wb') as new_file:
        new_file.write(downloaded_file)
    bot.send_message(msg.from_user.id, f"аудитория {aud} добаленна")


@bot.message_handler(content_types=["text"])
def path(msg):
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    r = f"SELECT CORP FROM USERS WHERE USER_ID = '{msg.from_user.id}'"
    corp = cur.execute(r).fetchone()
    if corp is None:
        bot.send_message(msg.from_user.id, text="У вас не выбран корпус\n /opt_structure")
        return
    corp = corp[0]
    file, err = find_path(corpus=str(corp), aud=msg.text)
    if not err:
        bot.send_message(msg.from_user.id,
                         text="Извините, что-то пошло не так\nВозможно мы еще не добавили эту аудиторию")
        return
    with open(file, 'rb') as video:
        bot.send_message(msg.from_user.id, f"Корпус: {corp} Аудитория: {msg.text}")
        bot.send_video(msg.from_user.id, video)


def main():
    print(bcolors.OKGREEN + 'Status: ' + bcolors.BOLD + 'Working' + bcolors.BOLD + bcolors.OKGREEN)
    print(bcolors.HEADER)
    bot.polling(none_stop=True, interval=0)
    print(bcolors.WARNING + 'Status: ' + bcolors.BOLD + 'Not Working' + bcolors.BOLD + bcolors.WARNING)


if __name__ == '__main__':
    main()
