import json
import xlrd
import re
import requests
import os
import sqlite3

def check_tags(tags, line):
    '''
    Поиск в строке одного из списка тегов. В случае нахождения тега, возвращает строку с этим тегом,
    и None в противном случае. Возвращает первый найденый тег.
    '''
    for i in tags:
        if re.search(i, line) != None:
            return i
    return None




if __name__ == "__main__":

    # Подсасывает все xlsx ссылки с сайта института
    link_MireaShedule = "https://www.mirea.ru/schedule/"
    with open("links.txt", "w", encoding='utf-8') as f:
        template_link = r"(https:\/\/.*\/(.*.xlsx))"
        res = requests.get(link_MireaShedule)
        print("LINK=" + link_MireaShedule, "CODE="+ str(res.status_code), sep=" ")
        find = re.findall(template_link, res.text)
        for link in find:
            f.write(link[0] + "\n")




    # Генерит все файлы xlsx
    try:    
        os.makedirs("xl")
    except:
        pass

    with open("links.txt", "r", encoding="utf-8") as f:
        template_XlNames = r".*\/(.*.xlsx)"
        for link in f.readlines():
            filename = re.findall(template_XlNames, link)
            
            

            link = link.strip()
            res = requests.get(link)
            print("LINK=" + link, "CODE="+ str(res.status_code), sep=" ")
            with open("./xl/" + filename[0], "wb") as f:
                f.write(res.content)



    # Крутим все файлы xlsx
    block_tags = [  # Список тегов, которые не будут обрабатыватся
        "Колледж",  # Расписание колледжа
        "Экз",      # Расписание экзаменов
        "сессия",   # Расписание экзаменов
        "З",        # Заочники
        "заоч",     # Заочники 
        "О-З"       # Очно-заочники
              
    ]

    special_tags = [ # Теги, для которых предусмотрена специальная обработка
        "Маг", # Магистратура
        "маг"  # Магистратура
    ]

    try:    
        os.makedirs("json")
    except:
        pass

    template_group = r".*-\d{2}-\d{2}.*" # Регулярка для формата групп
    groups_shedule = {}
    full_groups_shedule = {}

    
    for filename in os.listdir("./xl"):
        if check_tags(block_tags, filename) != None:
            continue
        groups_shedule.clear()
        
        # * Открываем эксель таблицу * # 
        rb = xlrd.open_workbook("./xl/" + filename)
        sheet = rb.sheet_by_index(0)
        
        # * Открываем джсон для эксель таблицы
        col = 0
        now_tag = check_tags(special_tags, filename)
        
        # * Крутим все группы, заполняем расписание * #
        for val in sheet.row_values(1):
            try:
                find = re.search(template_group, val)
                if find == None:
                    raise Exception
            except:
                col += 1
            else:
                col += 1
                groups_shedule[find.group(0)] = [[], [], [], [], [], []] # ! Записывает только имя группы. Все спецобозначения откидываются

                if now_tag == "Маг" or now_tag == "маг":
                    for k in range(5): 
                        day = sheet.col_values(col - 1, start_rowx=3 + 18 * k, end_rowx=21 + 18 * k)
                        groups_shedule[find.group(0)][k] = day
                    
                    day = sheet.col_values(col - 1, start_rowx=93, end_rowx=105)
                    groups_shedule[find.group(0)][5] = day
                    
                elif now_tag == None: # Дефолтный обработчик
                    for k in range(6): 
                        day = sheet.col_values(col - 1, start_rowx=3 + 12 * k, end_rowx=15 + 12 * k)
                        groups_shedule[find.group(0)][k] = day

        # * Записываем расписание в джсон * #
        with open("./json/" + filename[:-5] + ".json", "w", encoding="utf-8") as f:
            json.dump(groups_shedule, f, sort_keys=True, indent=4, ensure_ascii=False)   

        # full_groups_shedule = {**groups_shedule, **full_groups_shedule}                   # Можно сохранять полную базу, которую можно слить в один ОГРОМНЫЙ файл

        # * Cбрасываем рассписание * #
        groups_shedule.clear()  

        print("filename=" + filename, "Complete!", sep=" ")

        # with open("./json/AllInOne.json", "w", encoding="utf-8") as f:                        # Создание одной большой базы
        #     json.dump(full_groups_shedule, f, sort_keys=True, indent=4, ensure_ascii=False)


    pass
    