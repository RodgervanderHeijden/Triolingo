import pandas as pd
from numpy import random, sum
import string


# Import the dataframe with all sentences (as of now Lexicon)
# TODO: change this to include the entire corpus of tatoeba or CLARIN
# see: http://clarin-pl.eu/en/home-page/
# see: http://nkjp.pl/index.php?page=14&lang=1
def import_lexicon():
    """
        Imports and returns the own data (open questions)
    """
#    return pd.read_csv("./backend/data/my_data/Lexicon.csv")
    global lexicon
    lexicon = True
    return pd.read_csv("./backend/data/my_data/clean_lexicon.csv", sep=';')


def import_tatoeba():
    """
        Imports and returns the tatoeba data (multiple choice)
    """
    global lexicon
    lexicon = False
    return pd.read_csv("./backend/data/tatoeba/tatoeba_sentences.csv")


def retrieve_all_correct_answers(sentenceID):
    """
        Given a sentence ID, it retrieves and returns all other correct answers.
    """
    possible_answers = []
    if lexicon == True:
        data = import_lexicon()
    elif lexicon == False:
        data = import_tatoeba()
    data = data.loc[data['sentenceID'] == sentenceID]
    for i, row in data.iterrows():
        if row['lang'] == 'en':
            possible_answers.append(row['sentence_en'])
        elif row['lang'] == 'nl':
            possible_answers.append(row['sentence_nl'])
    return possible_answers


def select_quiz_words(difficulty, number_of_questions, mode):
    """
        Creates and returns a small df of size (number_of_questions).
        Mode currently is used as proxy for sentence/word questions,
        will be changed in the future. Difficulty is not taken into
        account yet, also future work (see issue #14).
    """
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


def check_answers(given_answer, quiz_df, sentenceID):
    """
        Given answer and the sentenceID, check whether it is correct.
        First use question_number (as index of quiz_df) to find matching
        sentenceID, then call retrieve_all_correct_answers for that ID.
        If the provided answer is in the list of possible answers, it is
        correct (True), otherwise not (False). Return result.
    """
    possible_answers = retrieve_all_correct_answers(sentenceID)

    remove_punctuation = str.maketrans("", "", string.punctuation)
    cleaned_given_answer = given_answer.lower().translate(remove_punctuation)

    cleaned_correct_answers = []
    for possible_answer in possible_answers:
        # Using the same remove_punctuation translation as defined above
        cleaned_answer = possible_answer.lower().translate(remove_punctuation)
        cleaned_correct_answers.append(cleaned_answer)

    if cleaned_given_answer in cleaned_correct_answers:
        return True
    else:
        return False


def generate_answer_options(questionID):
    """
        In case of multiple choice questions, three incorrect options have to be selected.
        With just questionID, the first answer of all_correct_answers is taken (fewer args passed),
        and three random numbers are chosen for the incorrect options. Theoretically, if a question
        has multiple correct translations in the database, multiple options could be correct. However,
        as evaluation takes this into account, it will also be evaluated correctly, and no tricky
        edge case mitigation should be done to combat this unlikely event.
        Returns both the already shuffled list with 4 answer options and the index of a correct one.
    """
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

    for incorrect_answer in incorrect_answers:
        multiple_choice_options.append(incorrect_answer)
    random.shuffle(multiple_choice_options)
    index = [multiple_choice_options.index(x) for x in multiple_choice_options if x in all_correct_answers][0]
    return multiple_choice_options, index


def update_dataframe():
    """
        Stores the quiz (meta)data to the appropriate locations.
        To be implemented.
    """
    pass
