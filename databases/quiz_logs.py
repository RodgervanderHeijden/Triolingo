import sqlite3
import codecs
import csv
import pandas as pd
from datetime import datetime

CREATE_QUIZ_TABLE = "CREATE TABLE IF NOT EXISTS quizzes (sentenceIDs TEXT, questions TEXT, given_answers TEXT, " \
                    "result FLOAT, time_of_quiz DATETIME, difficulty TEXT, mode TEXT)"
dtype_dict = {'quizID': 'INTEGER',
              'sentenceIDs': 'BLOB',
              'questions': 'TEXT',
              'given_answers': 'TEXT',
              'result': 'FLOAT',
              'time_of_quiz': 'DATETIME',
              'difficulty': 'TEXT',
              'mode': 'TEXT'
              }
INSERT_QUIZ = "INSERT INTO quizzes (sentenceIDs, questions, given_answers, " \
              "result, time_of_quiz, difficulty, mode) VALUES (?, ?, ?, ?, ?, ?, ?);"

pd.set_option('display.width', 240)
pd.set_option('display.max_columns', 10)


def connect_quiz():
    return sqlite3.connect("./databases/triolingo.db")


def initialize_table():
    """Initialize the table and fill it with the earlier data. Should never run again."""
    conn = connect_quiz()
    with conn:
        conn.execute(CREATE_QUIZ_TABLE)

    with codecs.open(r"../backend/data/my_data/quiz_log.csv", 'r', 'utf-8') as f:
        quiz_logs_reader = csv.reader(f, delimiter=";", )
        df = pd.DataFrame(quiz_logs_reader)

    df.columns = ['quizID', 'sentenceIDs', 'questions', 'given_answers', 'result', 'time_of_quiz', 'difficulty', 'mode']
    df = df[['sentenceIDs', 'questions', 'given_answers', 'result', 'time_of_quiz', 'difficulty', 'mode']]
    df.to_sql(name='quizzes', con=conn, if_exists='replace',
              index=False, dtype=dtype_dict)

    # df_new = pd.read_sql('SELECT * FROM quizzes', con=conn)
    # print(eval(df_new['sentenceIDs'][0])[0])


def add_new_quiz(quiz):
    sentenceIDs = quiz.quiz_results['sentenceID'].tolist()
    questions = quiz.quiz_results['Question'].tolist()
    given_answers = quiz.quiz_results['Given answer'].tolist()
    result = quiz.quiz_results['correct'].tolist()
    time_of_quiz = datetime.now()
    difficulty = quiz.difficulty
    mode = quiz.mode

    conn = connect_quiz()
    with conn:
        conn.execute(INSERT_QUIZ, (str(sentenceIDs), str(questions), str(given_answers), str(result), time_of_quiz, difficulty, mode,))
        df_new = pd.read_sql('SELECT rowid, * FROM quizzes', con=conn)
        print(df_new)
