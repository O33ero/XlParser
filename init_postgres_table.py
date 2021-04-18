
import psycopg2
from psycopg2 import Error

cur = None # Cursor
con = None # Connection
def connect(): # Соединение с базой
    global con
    con = psycopg2.connect(
        database="schedule", 
        user="postgres", 
        password="superpassword", 
        host="localhost", 
        port="5432"
    )
    global cur
    cur = con.cursor()
    print("Database opened successfully, cursor is now in 'cur' varible")


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

def clear_table(): # Отчистка таблицы
    cur.execute('DELETE FROM SCHEDULE *')
    print("Successfully cleared table Schedule")

def delete_table(): # Удаление таблицы
    cur.execute('DROP TABLE SCHEDULE')
    print("Successfully deleted table Schedule")

def end(): # Закрытие соединения
    con.commit()
    con.close()


if __name__ == "__main__":
    connect()
    clear_table()
    # init_table()

    # delete_table()
    end()