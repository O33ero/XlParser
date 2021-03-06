import json
import xlrd
import re
import requests
import os
import psycopg2
from datetime import *

import tablemanager as tm
import settings.config as cfg


_ident = 0

def delete_xlfiles(dir="./xl/"):
    '''
    Удаляет все xlsx файлы из папки dir 
    '''
    for filename in os.listdir("./xl"):
        os.remove(dir + filename)

    print("All xlsx have been successfully removed!")


def update_MireaSchedule():
    '''
    Обновить всю базу расписания МИРЭА (перед обновлением стирает всю базу до нуля). Генерирует xlsx, json файлы, а также создает
    links.txt - список всех ссылок с сайта. Функция очень время затратная, поэтому лучше включать её только вручную, когда это необходимо. \n
    Функция сначала обрабатывает все файлы, и только после окончания работы загружает их в базу.  
    '''
    delete_xlfiles()
    get_links(cfg.link_MireaShedule, cfg.links_file)
    get_xlfiles(cfg.links_file)

    # full_groups_shedule = {}

    tm.clear_Schedule()
    con = tm.connect()
    

    for filename in os.listdir("./xl"):
        # * Полный список групп с расписанием * #
        groups_shedule = parse_xlfiles(filename, cfg.block_tags, cfg.special_tags, cfg.substitute_lessons)
        if groups_shedule == None:
            continue

        # * Записываем расписание в джсон * #
        # convert_in_json(groups_shedule, filename[:-5] + ".json")
        convert_in_postgres(groups_shedule, con)

        print("filename=" + filename, "Complete!", sep=" ")

        # full_groups_shedule = {**groups_shedule, **full_groups_shedule}                   # Можно сохранять полную базу, которую можно слить в один ОГРОМНЫЙ файл
        groups_shedule.clear() 


    # with open("./json/AllInOne.json", "w", encoding="utf-8") as f:                        # Создание одной большой базы
    #     json.dump(full_groups_shedule, f, sort_keys=True, indent=4, ensure_ascii=False)
    
    tm.end(con)
    print("Database closed and commited successfully")

def get_TodaySchedule(today, group):
    '''
    Возвращает расписание [список] группы на сегодня. Возвращает None, если вызов произошел в воскресенье.
    '''
    con = tm.connect()
    cur = tm.cursor(con)

    ZeroDay = date(cfg.semestr_start[0], cfg.semestr_start[1], cfg.semestr_start[2])
    delta_day = abs((today - ZeroDay).days)
    week_number = delta_day // 7 + 1
    even_week = _get_even_week(week_number)
    week_day = _get_week_day(today.weekday())
    if week_day == "ВО":
        return None
    
    cur.execute(
        f'''
        SELECT * FROM SCHEDULE
        WHERE grp='{group}' and day='{week_day}' and even='{even_week}'
        ORDER BY id;
        '''
    )


    result = []
    for answer in cur:
        weeks_av = answer[10]
        if week_number in weeks_av:
            result.append(answer)

    tm.end(con)
    return result

def get_TomorrowSchedule(today, group):
    '''
    Возвращает расписание [список] группы на сегодня. Возвращает None, если вызов произошел в воскресенье.
    '''
    td = date(today.year, today.month, today.day + 1)
    return get_TodaySchedule(td, group)

def get_WeekSchedule(today, group):
    '''
    Возвращает расписание [список] группы на неделю.
    '''
    con = tm.connect()
    cur = tm.cursor(con)

    ZeroDay = date(cfg.semestr_start[0], cfg.semestr_start[1], cfg.semestr_start[2])
    delta_day = abs((today - ZeroDay).days)
    
    week_number = delta_day // 7 + 1
    even_week = _get_even_week(week_number)

    cur.execute(
        f'''
        SELECT * FROM SCHEDULE
        WHERE grp='{group}' and even='{even_week}'
        ORDER BY id;
        '''
    )

    result = []
    for answer in cur:
        weeks_av = answer[10]
        if week_number == weeks_av or week_number in weeks_av:
            result.append(answer)

    tm.end(con)
    return result

def get_WeekNumber(today):
    '''
    Возвращает номер недели.
    '''
    ZeroDay = date(cfg.semestr_start[0], cfg.semestr_start[1], cfg.semestr_start[2])
    delta_day = abs((today - ZeroDay).days)
    return delta_day // 7 + 1

def get_ExamsSchedule(group):
    con = tm.connect()
    cur = tm.cursor(con)

    cur.execute(
        f'''
        SELECT * FROM EXAMS
        WHERE grp='{group}'
        ORDER BY id;
        '''
    )
    result = cur.fetchall()
    tm.end(con)
    return result

def check_GroupExist(group):
    '''
    Проверяет существование группы в базе
    '''

    cur = tm.select_group(cur, group)

    if len(cur) == 0:
        return False
    else:
        return True




def _check_tags(tags, line):
    '''
    Поиск в строке одного из списка тегов. В случае нахождения тега, возвращает строку с этим тегом,
    и None в противном случае. Возвращает первый найденый тег.
    '''
    for i in tags.keys():
        if re.search(i, line) != None:
            return tags[i]
    return None

def _get_week_day(day_number):
    if day_number == 0:
        return "ПОНЕДЕЛЬНИК"
    elif day_number == 1:
        return "ВТОРНИК"
    elif day_number == 2:
        return "СРЕДА"
    elif day_number == 3:
        return "ЧЕТВЕРГ"
    elif day_number == 4:
        return "ПЯТНИЦА"
    elif day_number == 5:
        return "СУББОТА"
    elif day_number == 6:
        return "ВОСКРЕСЕНЬЕ"

def _get_even_week(week_number):
    if week_number % 2 == 0:
        return "EVEN"
    else:
        return "ODD"

def get_links(link, filename="links.txt"):
    '''
    Достает с html-страницы все ссылки формата " http:\/\/ ... .xlsx "
    и записывает в файл links.txt.
    '''
    with open(filename, "w", encoding='utf-8') as f:
        res = requests.get(link)
        print("LINK=" + link, "CODE="+ str(res.status_code), sep=" ")
        if res.status_code == 404:
            print("Something went wrong!")
        else:
            find = re.findall(r"(https:\/\/.*\/(.*.xlsx))", res.text)
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
            if res.status_code == 404:
                print("Something went wrong!")
            else:
                with open("./xl/" + filename[0], "wb") as f:
                    f.write(res.content)

def parse_xlfiles(xlfilename, block_tags=[], special_tags=[], substitute_lessons=[]):
    '''
    Вытаскивает из xl-таблиц все группы и их расписание. Возвращает словарь dic[group]= [[Monday], [Tuesday], [Wednesday]...];\n
    Возвращает None если имя файла имеет block_tags. Также имеет обработчики для special_tags. Если special_tag не найден, 
    то используется стандартный обработчик.
    '''



    # --- Утильные функции --- #

    def _antidot(line, mod=1): # Отчистка от плохих символов
        try:
            if mod == 0:
                line = re.sub(r"\n", " ", line)
                line = re.sub(r" {2,}", " ", line) # Удаление первого вхождение
            line = line.strip()
            line = re.sub(r"\t", "", line)
            line = re.sub(r"\…+.*", "", line)
            # line = re.sub(r" {2,}$", " ", line) # Удаление последнего вхождения
        except:
            pass
        return line

    def _substitute(line): # Замена длинных обозначений на короткие
        nonlocal substitute_lessons
        for i in substitute_lessons:
            line = re.sub(i, substitute_lessons[i], line)
        return line

    def _weekslicer(day_lessons): # Обработчик влючения/исключения недель
        lesson, typ, audit, start_time, end_time, order, even, week = day_lessons
        if lesson == "":
            return day_lessons
        arr = []
        find = re.match(r"кр\.? ([\d\, ]+)[нeд]{0,3}\.?", lesson) # кр. 12,15 н. 
        if find != None:
            try:
                find = re.findall(r"\d{1,2}", find.group(1))
                for each in find:
                    week.remove(int(each))
            except:
                pass
            finally:
                return (lesson, typ, audit, start_time, end_time, order, even, week)

        find = re.match(r"([\d\, \-\/н(лк)(пр)]+)[нeд]{0,3}\.?", lesson) # 12,15 н. или _12,15 н. или 12 , 15 н.
        if find != None:
            try:
                f = re.findall(r"(\d{1,2})[ ]*-[ ]*(\d{1,2})", find.group(1))
                for pair in f:
                    for i in range(int(pair[0]), int(pair[1]) + 1):
                        arr.append(i)
            except:
                pass
            try:
                f = re.findall(r"\d{1,2}", find.group(1))
                for each in f:
                    if int(each) not in arr:
                        arr.append(int(each))
            except:
                pass
            finally:
                week = arr
                week.sort()
                return (lesson, typ, audit, start_time, end_time, order, even, week)
        
        find = re.search(r"\(([\d\, \-\/н]+) [нед]{0,3}\.?\)", lesson) # (12,15 н.)
        if find != None:
            try:
                f = re.findall(r"(\d{1,2})[ ]*-[ ]*(\d{1,2})", find.group(1))
                for pair in f:
                    for i in range(int(pair[0]), int(pair[1]) + 1):
                        arr.append(i)
            except:
                pass
            try:
                f = re.findall(r"\d{1,2}", find.group(1))
                for each in f:
                    if int(each) not in arr:
                        arr.append(int(each))
            except:
                pass
            finally:
                week = arr
                week.sort()
                return (lesson, typ, audit, start_time, end_time, order, even, week)

        find = re.search(r"\(кр. ([\d\, ]+)[нед]{0,3}\.?\)", lesson) # (кр. 12,15 н.) 
        if find != None:
            try:
                find = re.findall(r"\d{1,2}", find.group(1))
                for each in find:
                    week.remove(int(each))
            except:
                pass
            finally:
                return (lesson, typ, audit, start_time, end_time, order, even, week)
        return day_lessons # Ничего не нашли

    def _recurparser(line):
        try:
            line = line.rstrip()
            find = re.search(r"(.*)( {4,}|\n|;)(.*)", line) # Нарезаем строку на два блока: (Голова) + (Последний предмет)
        except:
            find = None
        result = []

        if find == None:
            result.append(_antidot(line, 0))
            return result
        else:
            result.extend(_recurparser(find.group(1))) # Еще раз нарезаем первую половину, а потом еще и еще, пока не останется один элемент
            result.append(find.group(3)); # Добавляем в конец вторую половину (там гарантированно только 1 предмет)
            return result

    def _twiceschedule(obj): # Обрабочкик двойных объектов на одном слоте
        new_objs = []
        
        lesson = obj[0]
        typ = obj[1]
        audit = obj[2]

        lesson_arr = _recurparser(lesson)

        if len(lesson_arr) == 1:
            obj[2] = _antidot(obj[2],0)
            obj[0] = _antidot(obj[0],0)
            new_objs.append(obj)
        else:
            typ_arr = _recurparser(typ)
            audit_arr = _recurparser(audit)
            for i in range(len(lesson_arr)):
                lesson = lesson_arr[i]
                try:
                    typ = typ_arr[i]
                except:
                    typ = typ_arr[len(typ_arr) - 1]
                
                try:
                    audit = audit_arr[i]
                except:
                    audit = audit_arr[len(audit_arr) - 1]

                new_objs.append((lesson, typ, audit, obj[3], obj[4], obj[5], obj[6], obj[7]))
        return new_objs

    def _default_handler(): # Стандартный обработчик 
        nonlocal sheet, groups_shedule, find, col, time_schedule
        for k in range(6): 
            day_lesson = sheet.col_values(col - 1, start_rowx=3 + 12 * k, end_rowx=15 + 12 * k) # Делаем срез предметов
            type_lesson = sheet.col_values(col, start_rowx=3 + 12 * k, end_rowx=15 + 12 * k) # Делаем срез типа заняний (пр, лекция, лаб)
            audit_lesson = sheet.col_values(col + 2, start_rowx=3 + 12 * k, end_rowx=15 + 12 * k) # Делаем срез аудиторий

            for i in range(len(day_lesson)): # Убираем плохие символы 
                day_lesson[i] = _antidot(day_lesson[i], 1)
                day_lesson[i] = _substitute(day_lesson[i])
                type_lesson[i] = _antidot(type_lesson[i])
                audit_lesson[i] = _antidot(audit_lesson[i])
            
            evenodd = 1
            order = 1
            week = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
            schedule = []
            time_iter = iter(time_schedule)

            for i in range(len(day_lesson)):
                lesson = day_lesson[i]
                typ = type_lesson[i]
                audit = audit_lesson[i]
                time = next(time_iter)
                if evenodd % 2 == 0:
                    eo = "EVEN"
                else:
                    eo = "ODD"
                obj = [lesson, typ, audit, time[0], time[1], int(order), eo, week.copy()] # Объединяем все в один кортеж
                
                obj_arr = _twiceschedule(obj)
                for i in range(len(obj_arr)):
                    obj_arr[i] = _weekslicer(obj_arr[i])

                schedule.extend(obj_arr) 
                evenodd += 1
                order += 0.5
            
            groups_shedule[find.group(1)][k] = schedule

    def _mag_handler(): # Обработчик магистров
        nonlocal sheet, groups_shedule, find, col, time_schedule
        for k in range(5): 
            day_lesson = sheet.col_values(col - 1, start_rowx=3 + 18 * k, end_rowx=21 + 18 * k) # Делаем срез предметов
            type_lesson = sheet.col_values(col, start_rowx=3 + 18 * k, end_rowx=21 + 18 * k) # Делаем срез типа заняний (пр, лекция, лаб)
            audit_lesson = sheet.col_values(col + 2, start_rowx=3 + 18 * k, end_rowx=21 + 18 * k) # Делаем срез аудиторий

            for i in range(len(day_lesson)):# Убираем плхие символы и т.д.
                day_lesson[i] = _antidot(day_lesson[i], 1)
                day_lesson[i] = _substitute(day_lesson[i])
                type_lesson[i] = _antidot(type_lesson[i])
                audit_lesson[i] = _antidot(audit_lesson[i])
            
            evenodd = 1
            order = 1
            week = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
            schedule = []
            time_iter = iter(time_schedule)
            for i in range(len(day_lesson)):
                lesson = day_lesson[i]
                typ = type_lesson[i]
                audit = audit_lesson[i]
                time = next(time_iter)
                if evenodd % 2 == 0:
                    eo = "EVEN"
                else:
                    eo = "ODD"
                obj = [lesson, typ, audit, time[0], time[1], int(order), eo, week.copy()] # Объединяем все в один кортеж
                
                obj_arr = _twiceschedule(obj)
                for i in range(len(obj_arr)):
                    obj_arr[i] = _weekslicer(obj_arr[i])

                schedule.extend(obj_arr) 
                evenodd += 1
                order += 0.5
            
            groups_shedule[find.group(1)][k] = schedule
        
        # Делаем срез для субботы
        day_lesson = sheet.col_values(col - 1, start_rowx=93, end_rowx=105)
        type_lesson = sheet.col_values(col, start_rowx=93, end_rowx=105)
        audit_lesson = sheet.col_values(col + 2, start_rowx=93, end_rowx=105)
        for i in range(len(day_lesson)): # Убираем плхие символы и т.д.
            day_lesson[i] = _antidot(day_lesson[i], 1)
            day_lesson[i] = _substitute(day_lesson[i])
            type_lesson[i] = _antidot(type_lesson[i])
            audit_lesson[i] = _antidot(audit_lesson[i])
        
        evenodd = 1
        time_iter = iter(time_schedule)
        schedule = []
        for i in range(len(day_lesson)):
            lesson = day_lesson[i]
            typ = type_lesson[i]
            audit = audit_lesson[i] 
            time = next(time_iter)
            if evenodd % 2 == 0:
                eo = "EVEN"
            else:
                eo = "ODD"
            obj = [lesson, typ, audit, time[0], time[1], int(order), eo, week.copy()] # Объединяем все в один кортеж
            
            obj_arr = _twiceschedule(obj)
            for i in range(len(obj_arr)):
                obj_arr[i] = _weekslicer(obj_arr[i])

            schedule.extend(obj_arr) 
            evenodd += 1
            order += 0.5
        groups_shedule[find.group(1)][5] = schedule

    def _exams_handler(): #Обработчик экзаменов
        nonlocal sheet, groups_shedule, find, col
        day_exams = []
        time_exams = []
        audit_exams = []
        day_exams.extend(sheet.col_values(col - 1, start_rowx=2 , end_rowx=75))
        time_exams.extend(sheet.col_values(col, start_rowx=2 , end_rowx=75))
        audit_exams.extend(sheet.col_values(col + 1, start_rowx=2 , end_rowx=75))

        for i in range(len(day_exams)): # Убираем плхие символы и т.д.
            day_exams[i] = _antidot(day_exams[i], 0)
            day_exams[i] = _substitute(day_exams[i])
            time_exams[i] = _antidot(time_exams[i], 0)
            audit_exams[i] = _antidot(audit_exams[i], 0)
            

        date_exams = sheet.col_values(1, start_rowx=2, end_rowx=75)
        for i in range(len(date_exams)):
            date_exams[i] = _antidot(date_exams[i], 0)
        schedule = []
        exams_types = ["Экзамен", "Консультация", "Зачет", "Зачёт", "Зачёт диф.", "Диф. зачет", "Курсовая работа", "КП"]
        for i in range(0, len(day_exams)):
            typ = day_exams[i]
            if typ == "Экзамен" or typ == "Консультация" or typ == "Зачет" or typ == "Зачёт" or typ == "Зачёт диф." or typ == "КП":
                exam = day_exams[i + 1]
                lector = day_exams[i + 2]
                time = time_exams[i]
                audit = audit_exams[i]
                date = date_exams[i]
                obj = [date, exam, typ, lector, time, audit]
                schedule.append(obj)

            

        groups_shedule[find.group(1)] = schedule


        
    

    # --- Основная часть функции --- #

    if _check_tags(cfg.block_tags, xlfilename) != None:
        return None

    groups_shedule = {}    
    time_schedule = []
    
    # * Открываем эксель таблицу * # 
    rb = xlrd.open_workbook("./xl/" + xlfilename)

    for i in range(4):
        sheet = rb.sheet_by_index(i)
        try:
            sheet.row_values(1)
        except:
            continue
        else:
            break
    
    col = 0
    now_tag = _check_tags(special_tags, xlfilename)

    if now_tag == "маг":
        start_slice = sheet.col_values(2, start_rowx=3, end_rowx=21)
        end_slice = sheet.col_values(3, start_rowx=3, end_rowx=21)
    elif now_tag == None:
        start_slice = sheet.col_values(2, start_rowx=3, end_rowx=15)
        end_slice = sheet.col_values(3, start_rowx=3, end_rowx=15)

    if now_tag == None or now_tag == "маг":
        for time in start_slice:
            if time != '':
                time_schedule.append(time)
            else:
                time_schedule.append(time_schedule[len(time_schedule) - 1])
        i = 0
        for time in end_slice:
            if time != '':
                time_schedule[i] = (time_schedule[i], time)
            else:
                time_schedule[i] = time_schedule[i - 1]
            i += 1

    
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
            

            if  now_tag == "маг":
                groups_shedule[find.group(1)] = [[], [], [], [], [], []] # ! Записывает только имя группы. Все спецобозначения откидываются
                _mag_handler()
            elif now_tag == "экз":
                groups_shedule[find.group(1)] = []
                _exams_handler()
            else:
                groups_shedule[find.group(1)] = [[], [], [], [], [], []] # ! Записывает только имя группы. Все спецобозначения откидываются
                _default_handler()

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

def convert_in_postgres(group_schedule, con):
    '''
    Записывает в базу PostgreSQL расписание группы.
    '''
    global _ident
    for group in group_schedule.keys():
        if len(group_schedule[group][0]) == 6: # Значит расписание экзаменов
            tag = "Exams"
            break
        else:
            tag = "Schedule"
            break

    if tag == "Exams":
        cursor = con.cursor()
        for group in group_schedule.keys():
            for day_info in group_schedule[group]:
                date, exam, typ, lector, time, audit = day_info

                idn = str(_ident)
                cursor.execute(
                        f'''
                        INSERT INTO EXAMS (ID,GRP,DAY,EXAM,TYPE,LECTOR,TIME,AUDIT)
                        VALUES({idn},'{group}','{date}','{exam}','{typ}','{lector}','{time}','{audit}')
                        '''
                    )
                _ident += 1
                con.commit()  # Чтоб не ломать базу, лучше сначала все добавить в execute, а потом сделать commit
    else:
        cursor = con.cursor()
        days = ["ПОНЕДЕЛЬНИК", "ВТОРНИК", "СРЕДА", "ЧЕТВЕРГ", "ПЯТНИЦА", "СУББОТА"]
        days_iter = iter(days)

        for group in group_schedule.keys():
            days_iter = iter(days)
            for day in group_schedule[group]:
                day_now = next(days_iter)
                for lesson_info in day:
                    lesson, typ, audit, start_time, end_time, order, even, week = lesson_info
                    
                    strweek = [str(i) for i in week]
                    strweek = "{" + ",".join(strweek) + "}"
                    
                    
                    idn = str(_ident)
                    cursor.execute(
                        f'''
                        INSERT INTO SCHEDULE (ID,GRP,DAY,LESSON,TYPE,AUDIT,START_TIME,END_TIME,ORD,EVEN,WEEK)
                        VALUES({idn},'{group}','{day_now}','{lesson}','{typ}','{audit}','{start_time}','{end_time}','{order}','{even}','{strweek}')
                        '''
                    )
                    _ident += 1
                    con.commit()  # Чтоб не ломать базу, лучше сначала все добавить в execute, а потом сделать commit
    
    


if __name__ == "__main__":
    _ident = 0
    
    update_MireaSchedule()
    today = date.today()
    grp = 'ККСО-01-19'

    if True:
        schedule = get_WeekSchedule(today, grp)
        print(schedule)
    else:
        pass
    pass
    