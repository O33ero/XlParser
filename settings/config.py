'''
Переменные настройки для parser.
'''

link_MireaShedule = "https://www.mirea.ru/schedule/"
links_file = "links.txt"

first_september = [2020, 9, 1]
first_january = [2021, 1, 1]
semestr_start = [2021, 2, 8]

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
    "маг"       # Магистратура
]

substitute_lessons = {
    r"Физическая культура и спорт" : "Физ-ра",
    r"Иностранный язык" : "Ин.яз.",
    r"Специальные разделы дискретной математики" : "Дискретная математика",
    r"Математический анализ" : "Мат. анализ",
    r"Линейная алгебра и [(аналитическая геометрия), (АГ)]" : "Лин. ал.",
    r"Начертательная геометрия, инженерная и компьютерная графика" : "Инж. граф.",
    r"Алгебраические модели в информационной безопасности" : "Алгебра",
    r"День" : "",
    r"самостоятельных" : "",
    r"занятий" : "",
    r"день самостоятельной работы" : ""
}    


