
import psycopg2
from psycopg2 import Error

def connect(): # Соединение с базой
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
    return con.cursor()


def init_table(): # Инициализация таблицы
    cur.execute('''CREATE TABLE SCHEDULE  
            (ID INT PRIMARY KEY NOT NULL,
            GRP TEXT,
            DAY TEXT,
            LESSON TEXT,
            TYPE TEXT,
            AUDIT TEXT,
            ORD INT,
            EVEN TEXT,
            WEEK INT[]);''') 
    print("Successfully created table Schedule")

def clear_table(cur): # Отчистка таблицы
    cur.execute('DELETE FROM SCHEDULE *')
    print("Successfully cleared table Schedule")

def delete_table(cur): # Удаление таблицы
    cur.execute('DROP TABLE SCHEDULE')
    print("Successfully deleted table Schedule")

def end(con): # Закрытие соединения
    con.commit()
    con.close()


if __name__ == "__main__":
    con = connect()
    cur = cursor(con)
    clear_table(cur)
    # init_table()

    # delete_table()
    end(con)