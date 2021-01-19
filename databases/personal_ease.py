import sqlite3
import codecs
import csv
import pandas as pd

pd.set_option('display.width', 160)
pd.set_option('display.max_columns', 10)


# Tatoeba sentences plus personal ease added.
def connect_personal_sentences():
    return sqlite3.connect("triolingo.db")


CREATE_PERSONAL_TABLE = "CREATE TABLE IF NOT EXISTS personal_ease (sentenceID INTEGER, sentence_pl TEXT," \
                        "sentence_en TEXT, sentence_nl TEXT, lang TEXT, words_in_sentence TEXT," \
                        "sentence_ease FLOAT, personal_sentence_ease FLOAT)"


def initialize_table():
    """Initialize the table and fill it with the earlier data. Should never run again."""
    with codecs.open(r"../backend/data/tatoeba/quiz_df.csv", 'r', 'utf-8') as f:
        quiz_logs_reader = csv.reader(f, delimiter=",", )
        next(quiz_logs_reader, None) # to skip over the first row containing column names
        df = pd.DataFrame(quiz_logs_reader)
        df.columns = ['sentenceID', 'sentence_pl', 'sentence_en', 'sentence_nl', 'lang',
                      'words_in_sentence', 'sentence_ease', 'personal_sentence_ease']

    conn = connect_personal_sentences()
    with conn:
        conn.execute(CREATE_PERSONAL_TABLE)
        df.to_sql(name='personal_ease', con=conn, if_exists='replace', index=False)


conn = connect_personal_sentences()
with conn:
    conn.execute("UPDATE personal_ease SET personal_sentence_ease = 10948 WHERE rowid = 1;")
    df_new = pd.read_sql('SELECT * FROM personal_ease', con=conn)
    #print(df_new)

# change personal sentence ease hier
def change_personal_sentence_ease():
    conn = connect_personal_sentences()
    with conn:
        multi_factor = 1
        for sentenceID in [3942964, 7703669]:
        #     sql_update_query = "UPDATE personal_ease SET personal_sentence_ease = personal_sentence_ease*? WHERE sentenceID = ?"
        #     data = (multi_factor, sentenceID)
        #     conn.execute(sql_update_query, data).fetchall()

            sql_update_query = "SELECT lang FROM personal_ease WHERE sentenceID = ?;"
            data = (sentenceID)
            print(conn.execute(sql_update_query, (data,)).fetchall())
#        return connection.execute(GET_BEANS_BY_NAME, (name,)).fetchall()


change_personal_sentence_ease()