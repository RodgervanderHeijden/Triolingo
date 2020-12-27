import pandas as pd
from numpy import random, sum


# Import the dataframe with all sentences (as of now Lexicon)
# TODO: change this to include the entire corpus of tatoeba or CLARIN
# see: http://clarin-pl.eu/en/home-page/
# see: http://nkjp.pl/index.php?page=14&lang=1
def import_lexicon():
    return pd.read_csv("./backend/data/my_data/Lexicon.csv")


def import_tatoeba():
    return pd.read_csv("./backend/data/tatoeba/tatoeba_sentences.csv")


def retrieve_possible_answers(sentenceID):
    possible_answers = []
    data = import_tatoeba()
    data = data.loc[data['sentenceID'] == sentenceID]
    for i, row in data.iterrows():
        if row['lang'] == 'en':
            possible_answers.append(row['sentence_en'])
        elif row['lang'] == 'nl':
            possible_answers.append(row['sentence_nl'])
    return possible_answers


# Selecting what words are to be quizzed, based on the desired difficulty and quantity
def select_quiz_words(difficulty, number_of_questions):
    if difficulty == 'mastery':
        df = import_tatoeba()
    else:
        df = import_lexicon()

    # TODO: create meaningful weights, based on mastery ánd difficulty
    # Weights: mastery of word
    weights = len(df) * [1]
    cum_weights = weights/sum(weights)
    choice_list = random.choice(a=range(len(df)), size=number_of_questions,
                                replace=False, p=cum_weights)

    print(choice_list)
    # sentence_IDs = df.iloc[choice_list]['sentenceID']
    # print(sentence_IDs)
    chosen_words_df = df.iloc[choice_list]
    print(chosen_words_df)
    return chosen_words_df


def check_answers(given_answer, quiz_df, question_number):
    # _get_value uses index of total dataframe, while question_number is from 0 to (max_no_questions)
    # reset_index solved this, but is messy.
    quiz_df = quiz_df.reset_index()

    sentenceID = quiz_df._get_value(question_number, 'sentenceID')
    possible_answers = retrieve_possible_answers(sentenceID)

    if given_answer in possible_answers:
        print(given_answer, )
        print("Correct answer!")
        return True
    else:
        print(given_answer, )
        print("Incorrect answer!")
        return False

    # print(quiz_df._get_value(question_number, 'Dutch'), quiz_df._get_value(question_number, 'English'))
    # print(given_answer, type([quiz_df._get_value(question_number, 'Dutch')]), type(quiz_df._get_value(question_number, 'English')))
    # print(given_answer, quiz_df._get_value(question_number, 'Dutch'), quiz_df._get_value(question_number, 'English'))
    # print(given_answer, quiz_df._get_value(question_number, 'Dutch'), quiz_df._get_value(question_number, 'English'))

    # try:
    #     if (given_answer in quiz_df._get_value(question_number, 'Dutch')) or (given_answer in quiz_df._get_value(question_number, 'English')):
    #         print(given_answer,)
    #         print("Correct answer!")
    #         return True
    #     else:
    #         print(given_answer, quiz_df._get_value(question_number, 'Dutch'), quiz_df._get_value(question_number, 'English'))
    #         print("Incorrect answer!")
    #         return False
    # except:
    #     return False


# Write updates to the dataframe
def update_dataframe():
    pass
