import pandas as pd
from numpy import random, sum


# Import the dataframe with all sentences (as of now Lexicon)
# TODO: change this to include the entire corpus of tatoeba or CLARIN
# see: http://clarin-pl.eu/en/home-page/
# see: http://nkjp.pl/index.php?page=14&lang=1
def import_lexicon():
#    return pd.read_csv("./backend/data/my_data/Lexicon.csv")
    return pd.read_csv("./backend/data/my_data/clean_lexicon.csv", sep=';')


def import_tatoeba():
    return pd.read_csv("./backend/data/tatoeba/tatoeba_sentences.csv")


def retrieve_all_correct_answers(sentenceID):
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
def select_quiz_words(difficulty, number_of_questions, mode):
    if mode == 'multiple choice':
        df = import_tatoeba()
    elif mode == 'open':
        df = import_lexicon()

    # TODO: create meaningful weights, based on mastery ánd difficulty
    # Weights: mastery of word
    weights = len(df) * [1]
    cum_weights = weights/sum(weights)
    choice_list = random.choice(a=range(len(df)), size=number_of_questions,
                                replace=False, p=cum_weights)

    chosen_words_df = df.iloc[choice_list]
    return chosen_words_df


def check_answers(given_answer, quiz_df, question_number):
    # _get_value uses index of total dataframe, while question_number is from 0 to (max_no_questions)
    # reset_index solved this, but is messy.
    quiz_df = quiz_df.reset_index()

    sentenceID = quiz_df._get_value(question_number, 'sentenceID')
    possible_answers = retrieve_all_correct_answers(sentenceID)

    if given_answer in possible_answers:
        return True
    else:
        return False


def generate_answer_options(questionID):
    multiple_choice_options = []

    all_correct_answers = retrieve_all_correct_answers(questionID)
    multiple_choice_options.append(all_correct_answers[0])

    df = import_tatoeba()
    three_random_numbers = random.choice(a=range(len(df)), size=3,
                                replace=False)
    incorrect_answers = []
    for i, row in df.iloc[three_random_numbers].iterrows():
        if row['lang'] == 'en':
            incorrect_answers.append(row['sentence_en'])
        elif row['lang'] == 'nl':
            incorrect_answers.append(row['sentence_nl'])

    #multiple_choice_options.append(incorrect_answers.values)
    return all_correct_answers[0], incorrect_answers


# Write updates to the dataframe
def update_dataframe():
    pass
