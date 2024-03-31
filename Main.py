import telebot
import sqlite3
import os

from SECRET import TG_KEY, ADMINS, VIDEO_CHAT_ID, TEXT_CHAT_ID
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

ALL_FACK = [
    ('Агрономический факультет', 'https://www.vavilovsar.ru/upravlenie-obespecheniya-kachestva-obrazovaniya/struktura/otdel-organizacii-uchebnogo-processa-uk-№1/otdel-organizacii-uchebnogo-processa-uk-№-1/raspisanie-zanyatii-na-1-semestr-2013-2014-uchebno/agronomicheskii-fakultet/ochnaya-forma-obucheniya'),
    ("Факультет экономики и менеджмента", 'https://www.vavilovsar.ru/upravlenie-obespecheniya-kachestva-obrazovaniya/struktura/otdel-organizacii-uchebnogo-processa-uk-№1/otdel-organizacii-uchebnogo-processa-uk-№-1/raspisanie-zanyatii-na-1-semestr-2013-2014-uchebno/fakultet-ekonomiki-i-menedjmenta/ochnaya-forma-obucheniya'),
    ("Факультет инженерии и природообустройства", "https://www.vavilovsar.ru/upravlenie-obespecheniya-kachestva-obrazovaniya/struktura/otdel-organizacii-uchebnogo-processa-uk-№1/otdel-organizacii-uchebnogo-processa-uk-№2/raspisanie-ekzamenov-na-2-semestr-2013-2014-uchebn/fakultet-injenerii-i-prirodoobustroistva/ochnaya-forma-obucheniya"),
    ("Факультет ветеринарной медицины, пищевых и биотехнологии", 'https://www.vavilovsar.ru/upravlenie-obespecheniya-kachestva-obrazovaniya/struktura/otdel-organizacii-uchebnogo-processa-uk-№1/otdel-organizacii-uchebnogo-processa-uk-№3/raspisanie-zanyatii-na-1-semestr-2013-2014-uchebno/fakultet-veterinarnoi-mediciny-pishchevyx-i-biotex/ochnaya-forma-obucheniya')
]

def is_admin(msg) -> bool:
    if msg.chat.id != VIDEO_CHAT_ID:
        return False
    return True

def is_admin_chat(msg) -> bool:
    if msg.chat.id != TEXT_CHAT_ID:
        return False
    return True


@bot.message_handler(commands=["!"])
def tnp(msg):
    print(msg.chat.id)

@bot.message_handler(commands=["start"])
def start(msg):
    bot.send_message(msg.from_user.id, """Привет, студент! Добро пожаловать в чат-бот, который поможет тебе быстро
и легко найти нужные аудитории и преподавателей в университете!

Просто выбери номер учебного корпуса и номер нужной аудитории или фамилию преподавателя,
и бот пришлет тебе видео-инструкцию о том, как добраться туда. Начальной точкой является гардероб,
так что не беспокойся – мы поможем тебе не заблудиться. Желаем успешных занятий!

В данный момент бот работает в тестовом режиме, и вы сможете найти информацию о доступных аудиториях: 
319,318,320,Профком ,228,230,239,241,
234,243,Музей,240,242,244,249,251,253,153,
153а,338а,338,337,335,336,340,342,344,348,
350,352,354,347,349,353,355,Гидравлика ,33,
Столовая,128,127,130,132,134,131,Буфет,Библиотека

Команды:
/opt_professor - найти профессора
/list - список всех добавленных аудиторий 
/opt_structure - выбрать корпус
/ret - Остановить любое действие
(Название аудитории) - найти путь""")
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    r = f"SELECT CORP FROM USERS WHERE USER_ID = '{msg.from_user.id}'"
    if cur.execute(r).fetchone() is None:
        r = f"INSERT INTO USERS(USER_ID, CORP) VALUES ('{msg.from_user.id}', {2})"
        cur.execute(r)
        con.commit()
        con.close()

@bot.message_handler(commands=["schedule"])
def schedule(msg):
    markup = types.InlineKeyboardMarkup([
        [types.InlineKeyboardButton(text=ALL_FACK[0][0], url=ALL_FACK[0][1])],
        [types.InlineKeyboardButton(text=ALL_FACK[1][0], url=ALL_FACK[1][1])],
        [types.InlineKeyboardButton(text=ALL_FACK[2][0], url=ALL_FACK[2][1])],
        [types.InlineKeyboardButton(text=ALL_FACK[3][0], url=ALL_FACK[3][1])],
    ]
    )
    bot.send_message(msg.from_user.id, "Расписание:", reply_markup=markup)
@bot.message_handler(commands=["up_professor"])
def g_caf(msg):
    if not is_admin_chat(msg):
        return
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    r = f"SELECT Caf FROM Kafed"
    ol_caf = cur.execute(r).fetchall()
    f = []
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in ol_caf:
        s = str(i[0])
        f.append(types.KeyboardButton(text=s))
    markup.add(*f, row_width=1)
    con.close()
    bot.send_message(msg.from_user.id, text="Выберите кафедру", reply_markup=markup)
    msg.chat.id = msg.from_user.id
    bot.register_next_step_handler(msg, g_prof)


def g_prof(msg):
    if msg.text == "/ret":
        return
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
    if msg.text == "/ret":
        return
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
    if msg.text == "/ret":
        return
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
    fs = []
    with open('videos.txt', mode='r', encoding='UTF-8') as f:
        s = [x.strip().split('=') for x in f.readlines()]
        for cor, cab, file in sorted(s):
            fs.append(cab)
    bot.send_message(msg.from_user.id, '\n'.join(fs))


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
    if msg.text == "/ret":
        return
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

@bot.message_handler(content_types=["video"])
def vid(msg):
    if not is_admin(msg):
        return
    file = msg.video.file_id
    corp_cab = msg.json["caption"].split()
    flag = False
    line = ""
    with open('videos.txt', mode='r', encoding='UTF-8') as f:
        s = [x.strip().split('=') for x in f.readlines()]
        for cor, c, fl in s:
            if c == corp_cab[1] and cor == corp_cab[0]:
                flag = True
                line += f'{corp_cab[0]}={c}={file}\n'
            else:
                line += f'{corp_cab[0]}={c}={fl}\n'
    if not flag:
        line += f"{corp_cab[0]}={c}={file}"
    line = line.strip()
    f = open("videos.txt", 'w', encoding='UTF-8')
    f.write(line)
    f.close()




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
    try:
        with open('videos.txt', mode='r', encoding='UTF-8') as f:
            s = [x.strip().split('=') for x in f.readlines()]
            for cor, cab, file in s:
                if cab == msg.text and cor == str(corp):
                    break
            else:
                bot.send_message(msg.from_user.id,
                                 text="Извините, что-то пошло не так\nВозможно мы еще не добавили эту аудиторию")
                return
    except:
        bot.send_message(msg.from_user.id, "Извините, что-то пошло не так")
    bot.send_message(msg.from_user.id, f"Корпус: {corp} Аудитория: {msg.text}")
    bot.send_video(msg.from_user.id, file)


def main():
    print(bcolors.OKGREEN + 'Status: ' + bcolors.BOLD + 'Working' + bcolors.ENDC)
    bot.polling(none_stop=True, interval=0)
    print(bcolors.FAIL + 'Status: ' + bcolors.BOLD + 'Not Working')


if __name__ == '__main__':
    main()
