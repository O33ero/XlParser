
import psycopg2
from psycopg2 import Error

def connect(): # Соединение с базой
    '''
    Возвращает дискриптор соединения к Schedule
    '''
    con = psycopg2.connect(
        database="schedule", 
        user="postgres", 
        password="superpassword", 
        host="localhost", 
        port="5432"
    )
    print("Database opened successfully")
    return con

def cursor(con):
    '''
    Возвращает курсор соединения.
    '''
    return con.cursor()

def _init_table(cur): # Инициализация таблицы
    '''
    Создать таблицу Schedule.
    '''
    cur.execute('''CREATE TABLE IF NOT EXISTS SCHEDULE  
            (ID INT PRIMARY KEY NOT NULL,
            GRP VARCHAR(16),
            DAY VARCHAR(16),
            LESSON VARCHAR(256),
            TYPE VARCHAR(32),
            AUDIT VARCHAR(32),
            START_TIME VARCHAR(8),
            END_TIME VARCHAR(8),
            ORD INT,
            EVEN VARCHAR(4),
            WEEK INT[]);''') 


    cur.execute('''CREATE TABLE IF NOT EXISTS EXAMS  
            (
                ID INT PRIMARY KEY NOT NULL,
                GRP VARCHAR(16),
                DAY VARCHAR(16),
                EXAM VARCHAR(256),
                TYPE VARCHAR(64),
                LECTOR VARCHAR (128),
                TIME VARCHAR(16),
                AUDIT VARCHAR(64));''') 
    print("Successfully created table Schedule and Exams")


def _clear_table(cur): # Отчистка таблицы
    '''
    Отчистка таблицы.
    '''
    cur.execute('DELETE FROM EXAMS *')
    cur.execute('DELETE FROM SCHEDULE *')
    print("Successfully cleared table Schedule")

def _delete_table(cur): # Удаление таблицы
    '''
    Удалить таблицу.
    '''
    cur.execute('DROP TABLE EXAMS')
    cur.execute('DROP TABLE SCHEDULE')
    print("Successfully deleted table Schedule and Exams")

def end(con): # Закрытие соединения
    '''
    Закрыть соединение.
    '''
    con.commit()
    con.close()

def clear_Schedule():
    '''
    Отчистить таблицу Schedule.
    '''
    con = connect()
    cur = cursor(con)
    _clear_table(cur)
    end(con)

def rebuild_Schedule():
    '''
    Удалить и пересоздать таблицу Schedule
    '''
    con = connect()
    cur = cursor(con)
    _delete_table(cur)
    _init_table(cur)
    end(con)

def create_Schedule():
    con = connect()
    cur = cursor(con)
    _init_table(cur)
    end(con)

def select_group_Schedule(cursor, group):
    query = """
        SELECT * FROM SCHEDULE
        WHERE grp=%s
        ORDER BY id;
    """
    cursor.execute(query, (group, ))
    return cursor.fetchall()

def select_group_Exams(cursor, group):
    query = """
        SELECT * FROM EXAMS
        WHERE grp=%s
        ORDER BY id;
    """
    cursor.execute(query, (group, ))
    return cursor.fetchall()

if __name__ == "__main__":
    rebuild_Schedule()
    clear_Schedule()

