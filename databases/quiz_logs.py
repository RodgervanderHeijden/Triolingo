import sqlite3
import codecs
import csv
import pandas as pd
import json

CREATE_QUIZ_TABLE = "CREATE TABLE IF NOT EXISTS quizzes (quizID INTEGER PRIMARY KEY, sentenceIDs BLOB," \
                    "questions TEXT, given_answers TEXT, result FLOAT, current_time DATETIME, " \
                    "difficulty TEXT, mode TEXT)"
# dtype_dict = {'quizID': 'INTEGER',
#               'sentenceIDs': 'BLOB',
#               'questions': 'TEXT',
#               'given_answers': 'TEXT',
#               'result': 'FLOAT',
#               'current_time': 'DATETIME',
#               'difficulty': 'TEXT',
#               'mode': 'TEXT'
# }

pd.set_option('display.width', 320)
pd.set_option('display.max_columns',10)


# Quiz log, not specified by user
def connect_quiz():
    return sqlite3.connect("triolingo.db")


def create_tables(connection):
    with connection:
        connection.execute(CREATE_QUIZ_TABLE)


with codecs.open(r"../backend/data/my_data/quiz_log.csv", 'r', 'utf-8') as f:
    quiz_logs_reader = csv.reader(f, delimiter=";", )
    df = pd.DataFrame(quiz_logs_reader)


# Store df into DB
conn = connect_quiz()
create_tables(conn)
#print(pd.read_sql('SELECT * FROM quizzes', con=conn))
df.columns = ['quizID', 'sentenceIDs', 'questions', 'given_answers', 'result', 'current_time', 'difficulty', 'mode']

df.to_sql(name='quizzes', con=conn, if_exists='replace',
          index=False) #, dtype=dtype_dict)

df_new = pd.read_sql('SELECT * FROM quizzes', con=conn)

print(df_new)
