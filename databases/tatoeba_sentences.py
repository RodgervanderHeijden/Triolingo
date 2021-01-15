import sqlite3
import codecs
import csv
import pandas as pd


# All tatoeba sentences + sentence ease
def connect_tatoeba_sentences():
    return sqlite3.connect("triolingo.db")

CREATE_TATOEBA_TABLE = "CREATE TABLE IF NOT EXISTS tatoeba (sentenceID INTEGER PRIMARY KEY)"

#sentenceID,sentence_pl,sentence_en,sentence_nl,lang,words_in_sentence,sentence_ease,personal_sentence_ease


def create_tables(connection):
    with connection:
        connection.execute(CREATE_TATOEBA_TABLE)


with codecs.open(r"../backend/data/tatoeba/quiz_df.csv", 'r', 'utf-8') as f:
    quiz_logs_reader = csv.reader(f, delimiter=";", )
    df = pd.DataFrame(quiz_logs_reader)

    # Store df into DB
    conn = connect_tatoeba_sentences()
    create_tables(conn)
    df.to_sql(name='tatoeba', con=conn, if_exists='replace', index=False)

df_new = pd.read_sql('SELECT * FROM tatoeba', con=conn)

print(df_new)
