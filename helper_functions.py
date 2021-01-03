import pandas as pd
import numpy as np
import string
from helper_classes import User, Quiz, Question

lexicon = bool()


# Import the dataframe with all sentences (as of now Lexicon)
# TODO: change this to include the entire corpus of tatoeba or CLARIN
# see: http://clarin-pl.eu/en/home-page/
# see: http://nkjp.pl/index.php?page=14&lang=1
def import_lexicon():
    """Import and return the own data (open questions)."""
    global lexicon
    lexicon = True
    return pd.read_csv("./backend/data/my_data/clean_lexicon.csv", sep=';')


def import_tatoeba():
    """Import and return the tatoeba data (multiple choice)."""
    global lexicon
    lexicon = False
    return pd.read_csv("./backend/data/tatoeba/quiz_df.csv").sort_values(by=['sentence_ease'], ascending=False)


def generate_answer_options(questionID, current_quiz, question):
    """Generates three incorrect answer options for multiple choice questions.

    In case of multiple choice questions, three incorrect options have to be selected.
    With just questionID, the first answer of all_correct_answers is taken (fewer args passed),
    and three random numbers are chosen for the incorrect options. Theoretically, if a question
    has multiple correct translations in the database, multiple options could be correct. However,
    as evaluation takes this into account, it will also be evaluated correctly, and no tricky
    edge case mitigation should be done to combat this unlikely event.
    Return both the already shuffled list with 4 answer options and the index of a correct one."""
    multiple_choice_options = []

    question.generate_correct_answers()
    print(questionID)
    print(question.correct_answers)
    print(multiple_choice_options)
    print(question.correct_answers[0])
    multiple_choice_options.append(question.correct_answers[0])

    df = import_tatoeba()
    three_random_numbers = np.random.choice(a=range(len(df)), size=3,
                                         replace=False)
    incorrect_answers = []
    for _, row in df.iloc[three_random_numbers].iterrows():
        if row['lang'] == 'en':
            incorrect_answers.append(row['sentence_en'])
        elif row['lang'] == 'nl':
            incorrect_answers.append(row['sentence_nl'])

    for incorrect_answer in incorrect_answers:
        multiple_choice_options.append(incorrect_answer)
    np.random.shuffle(multiple_choice_options)
    index = [multiple_choice_options.index(x) for x in multiple_choice_options if x in question.correct_answers][0]
    return multiple_choice_options, index


def convert_answer(given_answer):
    if given_answer.lower() in ['a', 'b', 'c', 'd', '1', '2', '3', '4']:
        # Is answer was given as letter, convert to numerical
        if given_answer.lower() == 'a':
            given_answer = 1
        elif given_answer.lower() == 'b':
            given_answer = 2
        elif given_answer.lower() == 'c':
            given_answer = 3
        elif given_answer.lower() == 'd':
            given_answer = 4
        given_answer = int(given_answer)
        # To convert to correct index, subtract one. This works both for the human-provided numbers
        # and the just mapped numbers.
        converted_answer = given_answer - 1
        return converted_answer


def check_answers(given_answer, sentenceID):
    """Check whether the user-provided answer is correct.

    Given answer and the sentenceID, check whether it is correct.
    First use question_number (as index of quiz_df) to find matching
    sentenceID, then call retrieve_all_correct_answers for that ID.
    If the provided answer is in the list of possible answers, it is
    correct (True), otherwise not (False). Return result."""
    possible_answers = retrieve_all_correct_answers(sentenceID)
    remove_punctuation = str.maketrans("", "", string.punctuation)
    cleaned_given_answer = given_answer.lower().translate(remove_punctuation)

    cleaned_correct_answers = []
    for possible_answer in possible_answers:
        # Using the same remove_punctuation translation as defined above
        cleaned_answer = possible_answer.lower().translate(remove_punctuation)
        cleaned_correct_answers.append(cleaned_answer)
    return cleaned_given_answer in cleaned_correct_answers


def expected_correct_ratio(difficulty):
    """Returns the expected ratio of correct questions."""
    if difficulty == "easy":
        return 0.8
    elif difficulty == "moderate":
        return 0.6
    elif difficulty == "difficult":
        return 0.3


def calculate_error(quiz_answers_correct, difficulty):
    y_hat = expected_correct_ratio(difficulty)
    score = sum(quiz_answers_correct)/len(quiz_answers_correct)
    error = (score-y_hat)
    return error


def update_dataframe(quiz_results):
    """Stores the quiz (meta)data to the appropriate locations. To be implemented."""
    df = import_tatoeba()
    for i, row in quiz_results.iterrows():
        print(df.loc[df['sentenceID'] == row['sentenceID']])
        data_row_index = df.loc[df['sentenceID'] == row['sentenceID']].index
        #print(data_row_index)
        print(f"data_row_index {data_row_index}")
        print(df.iloc[data_row_index])
        print("HIERBOVEN data row index in df iloc, hieronder de value")
        print(df.iloc[data_row_index]['personal_sentence_ease'])
        print("Hieronder dan weer een probeerseltje")
        print(df.loc[df['sentenceID'] == row['sentenceID']]['personal_sentence_ease'])

        if quiz_results['correct'][i]:
            df.loc[df['sentenceID'] == row['sentenceID']]['personal_sentence_ease'] = (
                                      df.loc[df['sentenceID'] == row['sentenceID']]['personal_sentence_ease']) * 1.25
            #df.at[data_row_index, 'personal_sentence_ease'] = (df.iloc[data_row_index]['personal_sentence_ease'].value) * 1.20
            print("hierfaga")
        else:
            df.loc[df['sentenceID'] == row['sentenceID']]['personal_sentence_ease'] = (
                                      df.loc[df['sentenceID'] == row['sentenceID']]['personal_sentence_ease']) * 0.80
#            df.at[data_row_index, 'personal_sentence_ease'] = df.iloc[data_row_index]['personal_sentence_ease'] * 0.80
            print("daraega")
        print(df.loc[data_row_index]['personal_sentence_ease'])
        print(df.loc[df['sentenceID'] == row['sentenceID']]['personal_sentence_ease'])


def after_quiz(user, quiz_results, difficulty):
    """Method to call after quiz has finished. Write results, calculate new scores."""
    error = calculate_error(quiz_results['correct'], difficulty)
    user.update_language_proficiency(error)

    #update_dataframe(quiz_results)
