
import psycopg2
from psycopg2 import Error

con = psycopg2.connect(
  database="schedule", 
  user="postgres", 
  password="superpassword", 
  host="localhost", 
  port="5432"
)
print("Database opened successfully")

cur = con.cursor()
# cur.execute('''CREATE TABLE SCHEDULE  # Вариант 1
#      (ID INT PRIMARY KEY NOT NULL,
#      GRP TEXT,
#      MONDAY TEXT[],
#      TUESDAY TEXT[],
#      WEDNESDAY TEXT[],
#      THURSDAY TEXT[],
#      FRIDAYE TEXT[],
#      SATURDAY TEXT[]);''')

cur.execute('''CREATE TABLE SCHEDULE  # Вариант 2
  (ID INT PRIMARY KEY NOT NULL,
  GRP TEXT,
  DAY TEXT,
  LESSON TEXT,
  TYPE TEXT,
  AUDIT TEXT);''')




print("Successfully created table Schedule")

con.commit()
con.close()