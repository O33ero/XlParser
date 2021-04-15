import json
import xlrd
import re
import requests
import os
import sqlite3

block_tags = [   # Список тегов, которые не будут обрабатыватся
        "Колледж",   # Расписание колледжа
        "Экз",       # Расписание экзаменов
        "сессия",    # Расписание экзаменов
        "З",         # Заочники
        "заоч",      # Заочники 
        "О-З"        # Очно-заочники
              
    ]
special_tags = [ # Теги, для которых предусмотрена специальная обработка
    "Маг",       # Магистратура
    "маг"        # Магистратура
]

def check_tags(tags, line):
    '''
    Поиск в строке одного из списка тегов. В случае нахождения тега, возвращает строку с этим тегом,
    и None в противном случае. Возвращает первый найденый тег.
    '''
    for i in tags:
        if re.search(i, line) != None:
            return i
    return None

def get_links(link, filename="links.txt"):
    '''
    Достает с html-страницы все ссылки формата " http:\/\/ ... .xlsx "
    и записывает в файл links.txt.
    '''
    with open(filename, "w", encoding='utf-8') as f:
        template_link = r"(https:\/\/.*\/(.*.xlsx))"
        res = requests.get(link)
        print("LINK=" + link, "CODE="+ str(res.status_code), sep=" ")
        find = re.findall(template_link, res.text)
        for link in find:
            f.write(link[0] + "\n")

def get_xlfiles(filename="links.txt"):
    '''
    Достает все ссылки из файла links.txt, создаем xl-таблицы, складываем их в папку.
    '''
    try:    
        os.makedirs("xl")
    except:
        pass

    with open("links.txt", "r", encoding="utf-8") as f:
        for link in f.readlines():
            filename = re.findall(r".*\/(.*.xlsx)", link)

            link = link.strip()
            res = requests.get(link)
            print("LINK=" + link, "CODE="+ str(res.status_code), sep=" ")
            with open("./xl/" + filename[0], "wb") as f:
                f.write(res.content)

def parse_xlfiles(xlfilename, block_tags=[], special_tags=[]):
    '''
    Вытаскивает из xl-таблиц все группы и их расписание. Возвращает словарь dic[group]= [[Monday], [Tuesday], [Wednesday]...];\n
    Возвращает None если имя файла имеет block_tags.
    Также имеет обработчики для special_tags. Если special_tag не найден, то используется стандартный обработчик. \n
    !!! Функция очень времязатратная, не рекомендуется вызывать её при каждом запросе к базе !!!
    '''




    def __default_handler(): # Стандартный обработчик 
        nonlocal sheet, groups_shedule, find, col
        for k in range(6): 
            day = sheet.col_values(col - 1, start_rowx=3 + 12 * k, end_rowx=15 + 12 * k)
            for i in range(len(day)):
                day[i] = re.sub(r"\n", " ", day[i])
            groups_shedule[find.group(1)][k] = day

    def __mag_handler(): # Обработчик магистров
        nonlocal sheet, groups_shedule, find, col
        modified_day = []
        for k in range(5): 
            day = sheet.col_values(col - 1, start_rowx=3 + 18 * k, end_rowx=21 + 18 * k)
            for i in range(len(day)):
                day[i] = re.sub(r"\n", " ", day[i])
            groups_shedule[find.group(1)][k] = day
        day = sheet.col_values(col - 1, start_rowx=93, end_rowx=105)
        for i in range(len(day)):
                day[i] = re.sub(r"\n", " ", day[i])
        groups_shedule[find.group(1)][5] = day





    if check_tags(block_tags, xlfilename) != None:
        return None

    groups_shedule = {}    
    
    # * Открываем эксель таблицу * # 
    rb = xlrd.open_workbook("./xl/" + xlfilename)
    sheet = rb.sheet_by_index(0)
    
    col = 0
    now_tag = check_tags(special_tags, xlfilename)
    
    # * Крутим все группы, заполняем расписание * #
    for now_val in sheet.row_values(1):
        try:
            find = re.search(r".*(....-\d{2}-\d{2}).*", now_val)
            if find == None:
                raise Exception
        except:
            col += 1
        else:
            col += 1
            groups_shedule[find.group(1)] = [[], [], [], [], [], []] # ! Записывает только имя группы. Все спецобозначения откидываются

            if now_tag == "Маг" or now_tag == "маг":
                __mag_handler()
            else:
                __default_handler()

    return groups_shedule

def convert_in_json(data, filename):
    '''
    Преобразует python-данные в формат json.
    '''
    try:    
        os.makedirs("json")
    except:
        pass
    with open("./json/" + filename, "w", encoding="utf-8") as f:
        json.dump(data, f, sort_keys=True, indent=4, ensure_ascii=False)  



if __name__ == "__main__":

    
    link_MireaShedule = "https://www.mirea.ru/schedule/"
    links_file = "links.txt"

    get_links(link_MireaShedule, links_file)
    get_xlfiles(links_file)

    
    full_groups_shedule = {}
    for filename in os.listdir("./xl"):
        # * Полный список групп с расписанием * #
        groups_shedule = parse_xlfiles(filename, block_tags, special_tags)
        if groups_shedule == None:
            continue

        # * Записываем расписание в джсон * #
        convert_in_json(groups_shedule, filename[:-5] + ".json")


        print("filename=" + filename, "Complete!", sep=" ")

        full_groups_shedule = {**groups_shedule, **full_groups_shedule}                   # Можно сохранять полную базу, которую можно слить в один ОГРОМНЫЙ файл
        groups_shedule.clear() 



    with open("./json/AllInOne.json", "w", encoding="utf-8") as f:                        # Создание одной большой базы
        json.dump(full_groups_shedule, f, sort_keys=True, indent=4, ensure_ascii=False)


    pass
    