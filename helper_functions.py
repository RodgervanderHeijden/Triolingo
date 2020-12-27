import pandas as pd
from numpy import random, sum


# Import the dataframe with all sentences (as of now Lexicon)
# TODO: change this to include the entire corpus of tatoeba or CLARIN
# see: http://clarin-pl.eu/en/home-page/
# see: http://nkjp.pl/index.php?page=14&lang=1
def import_lexicon():
    '''
        Imports and returns the own data (open questions)
    '''
#    return pd.read_csv("./backend/data/my_data/Lexicon.csv")
    return pd.read_csv("./backend/data/my_data/clean_lexicon.csv", sep=';')


def import_tatoeba():
    '''
        Imports and returns the tatoeba data (multiple choice)
    '''
    return pd.read_csv("./backend/data/tatoeba/tatoeba_sentences.csv")


def retrieve_all_correct_answers(sentenceID):
    '''
        Given a sentence ID, it retrieves and returns all other correct answers.
    '''
    possible_answers = []
    data = import_tatoeba()
    data = data.loc[data['sentenceID'] == sentenceID]
    for i, row in data.iterrows():
        if row['lang'] == 'en':
            possible_answers.append(row['sentence_en'])
        elif row['lang'] == 'nl':
            possible_answers.append(row['sentence_nl'])
    return possible_answers


def select_quiz_words(difficulty, number_of_questions, mode):
    '''
        Creates and returns a small df of size (number_of_questions).
        Mode currently is used as proxy for sentence/word questions,
        will be changed in the future. Difficulty is not taken into
        account yet, also future work (see issue #14).
    '''
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
    '''
        Given answer and the sentenceID, check whether it is correct.
        First use question_number (as index of quiz_df) to find matching
        sentenceID, then call retrieve_all_correct_answers for that ID.
        If the provided answer is in the list of possible answers, it is
        correct (True), otherwise not (False). Return result.
    '''
    sentenceID = quiz_df._get_value(question_number, 'sentenceID')
    possible_answers = retrieve_all_correct_answers(sentenceID)

    if given_answer in possible_answers:
        return True
    else:
        return False


def generate_answer_options(questionID):
    '''
        In case of multiple choice questions, three incorrect options have to be selected.
        With just questionID, the first answer of all_correct_answers is taken (fewer args passed),
        and three random numbers are chosen for the incorrect options. Theoretically, if a question
        has multiple correct translations in the database, multiple options could be correct. However,
        as evaluation takes this into account, it will also be evaluated correctly, and no tricky
        edge case mitigation should be done to combat this unlikely event.
    '''
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


def update_dataframe():
    '''
        Stores the quiz (meta)data to the appropriate locations.
        To be implemented.
    '''
    pass
