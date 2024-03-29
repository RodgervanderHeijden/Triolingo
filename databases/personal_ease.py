import sqlite3
import codecs
import csv
import pandas as pd
import numpy as np

CREATE_PERSONAL_TABLE = "CREATE TABLE IF NOT EXISTS personal_ease_pl (sentenceID INTEGER, sentence_pl TEXT," \
                        "sentence_en TEXT, sentence_nl TEXT, lang TEXT, words_in_sentence TEXT," \
                        "sentence_ease FLOAT, personal_sentence_ease FLOAT)"
UPDATE_USER_STATS = "UPDATE personal_ease_pl " \
                    "SET sentence_ease = ?, personal_sentence_ease = ? " \
                    "WHERE sentenceID IN {};"


# Tatoeba sentences plus personal ease added.
def connect_personal_sentences():
    return sqlite3.connect("./databases/triolingo.db")


def initialize_table():
    """Initialize the table and fill it with the earlier data. Should never run again."""
    with codecs.open(r"../backend/data/tatoeba/quiz_df.csv", 'r', 'utf-8') as f:
        quiz_logs_reader = csv.reader(f, delimiter=",", )
        next(quiz_logs_reader, None)  # to skip over the first row containing column names
        df = pd.DataFrame(quiz_logs_reader)
        df.columns = ['sentenceID', 'sentence_pl', 'sentence_en', 'sentence_nl', 'lang',
                      'words_in_sentence', 'sentence_ease', 'personal_sentence_ease']

    conn = connect_personal_sentences()
    with conn:
        conn.execute(CREATE_PERSONAL_TABLE)
        df.to_sql(name='personal_ease_pl', con=conn, if_exists='replace', index=False)


def return_chosen_sentenceIDs(list_chosen_sentence_rownumbers):
    """Given a list of indices (not rowid!), order db by difficulty and select those indices."""
    conn = connect_personal_sentences()
    with conn:
        result_set = conn.execute(
            'SELECT * '
            'FROM (SELECT row_number() OVER (ORDER BY personal_sentence_ease DESC) AS rowNum, * '
            'FROM personal_ease_pl)'
            'WHERE rowNum IN (%s)' %
            ','.join('?' * len(list_chosen_sentence_rownumbers)), list_chosen_sentence_rownumbers)
        column_list = ['rowNum', 'sentenceID', 'sentence_pl', 'sentence_en', 'sentence_nl', 'lang',
                       'words_in_sentence', 'sentence_ease', 'personal_sentence_ease']
        df_chosen_sentenceIDs = pd.DataFrame(result_set.fetchall(), columns=column_list)
    return df_chosen_sentenceIDs['sentenceID']


def get_question_sentence(sentenceID):
    conn = connect_personal_sentences()
    with conn:
        result = conn.execute('SELECT sentence_pl '
                              'FROM personal_ease_pl '
                              'WHERE sentenceID = ?', (sentenceID,)).fetchone()
    return result[0]


def select_answer_sentence(df):
    """Take the English sentence in case of English metadata, otherwise Dutch."""
    list_with_answers = []
    for _, row in df.iterrows():
        if row['language'] == 'en':
            list_with_answers.append(row['sentence_en'])
        elif row['language'] == 'nl':
            list_with_answers.append(row['sentence_nl'])
    return list_with_answers


def get_answer_options(sentenceID):
    """Take all correct sentences and randomly pick three incorrect ones."""
    conn = connect_personal_sentences()
    with conn:
        correct_options = conn.execute('SELECT sentence_en, sentence_nl, lang '
                                       'FROM personal_ease_pl '
                                       'WHERE sentenceID = ?', (sentenceID,)).fetchall()

    three_random_numbers = np.random.choice(a=range(60039), size=3, replace=False)
    number_one = three_random_numbers[0]
    number_two = three_random_numbers[1]
    number_three = three_random_numbers[2]
    conn = connect_personal_sentences()
    with conn:
        incorrect_options = conn.execute('SELECT sentence_en, sentence_nl, lang '
                                         'FROM (SELECT row_number() OVER('
                                         '      ORDER BY personal_sentence_ease DESC) AS rowNum, * '
                                         '      FROM personal_ease_pl) '
                                         'WHERE (rowNum = ? OR rowNum = ? OR rowNum = ?)',
                                         (int(number_one), int(number_two), int(number_three), )).fetchmany(3)

    column_names = ['sentence_en', 'sentence_nl', 'language']
    df_correct_options = pd.DataFrame(correct_options, columns=column_names)
    df_incorrect_options = pd.DataFrame(incorrect_options, columns=column_names)
    possible_correct_answers = select_answer_sentence(df_correct_options)
    incorrect_answer_options = select_answer_sentence(df_incorrect_options)
    return possible_correct_answers, incorrect_answer_options


def update_personal_sentence_ease(quiz_results):
    # Duplicate rows are thrown out, both because it's more convenient and because they repeat until correct
    # Thus, a question once answered incorrectly and subsequently answered correctly would end up with the
    # same personal difficulty (diff * 1.25 * 0.80).
    canon_quiz_results = quiz_results.drop_duplicates(subset=['sentenceID'], keep='first').reset_index()
    sentenceIDs = canon_quiz_results['sentenceID'].values
    conn = connect_personal_sentences()
    with conn:
        personal_sentence_eases = conn.execute("SELECT personal_sentence_ease, sentenceID "
                                               "FROM personal_ease_pl "
                                               "WHERE sentenceID IN (%s)" %
                                               ','.join('?' * len(sentenceIDs)), sentenceIDs).fetchall()
        for i in range(len(sentenceIDs)):
            # Since the personal sentence eases is a list of tuples (ease, ID), duplicate rows are not included.
            # Thus, when starting a quiz with an incorrect answer, there would be more sentenceIDs than elements.
            # By adding the if-statement below, the correct personal ease is taken.
            for j in range(len(personal_sentence_eases)):
                if sentenceIDs[i] == personal_sentence_eases[j][1]:
                    current_personal_sentence_ease = float(personal_sentence_eases[j][0])

            if canon_quiz_results.correct[i]:
                new_personal_sentence_ease = float(current_personal_sentence_ease * 1.25)
            else:
                new_personal_sentence_ease = float(current_personal_sentence_ease * 0.80)
                
            conn.execute("UPDATE personal_ease_pl "
                         "SET personal_sentence_ease = ? "
                         "WHERE sentenceID = ?", (new_personal_sentence_ease, sentenceIDs[i]))
