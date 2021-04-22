
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
            GRP TEXT,
            DAY TEXT,
            LESSON TEXT,
            TYPE TEXT,
            AUDIT TEXT,
            START_TIME TEXT,
            END_TIME TEXT,
            ORD INT,
            EVEN TEXT,
            WEEK INT[]);''') 
    print("Successfully created table Schedule")

def _clear_table(cur): # Отчистка таблицы
    '''
    Отчистка таблицы.
    '''
    cur.execute('DELETE FROM SCHEDULE *')
    print("Successfully cleared table Schedule")

def _delete_table(cur): # Удаление таблицы
    '''
    Удалить таблицу.
    '''
    cur.execute('DROP TABLE SCHEDULE')
    print("Successfully deleted table Schedule")

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

def select_group(cursor, group):
    query = """
        SELECT * FROM SCHEDULE
        WHERE grp=%s
        ORDER BY id;
    """
    cursor.execute(query, (group, ))
    return cursor.fetchall()


if __name__ == "__main__":
    create_Schedule()
    # clear_Schedule()

