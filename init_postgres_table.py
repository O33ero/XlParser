
import psycopg2
from psycopg2 import Error

cur = None # Cursor
con = None # Connection
def connect():
  con = psycopg2.connect(
    database="schedule", 
    user="postgres", 
    password="superpassword", 
    host="localhost", 
    port="5432"
  )
  cur = con.cursor()
  print("Database opened successfully, cursor is now in 'cur' varible")


def init_table():
  cur.execute('''CREATE TABLE SCHEDULE  
            (ID INT PRIMARY KEY NOT NULL,
            GRP TEXT,
            DAY TEXT,
            LESSON TEXT,
            TYPE TEXT,
            AUDIT TEXT,
            EVEN TEXT);''') # Вариант 2
  print("Successfully created table Schedule")

def end():
    con.commit()
    con.close()


if __name__ == "__main__":
    connect()
    init_table()
    end()