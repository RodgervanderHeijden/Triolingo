import pandas as pd
import numpy as np
import string
import scipy.stats as stats

lexicon = pd.DataFrame()


# Import the dataframe with all sentences (as of now Lexicon)
# TODO: change this to include the entire corpus of tatoeba or CLARIN
# see: http://clarin-pl.eu/en/home-page/
# see: http://nkjp.pl/index.php?page=14&lang=1
def import_lexicon():
    """Import and return the own data (open questions)."""
    #    return pd.read_csv("./backend/data/my_data/Lexicon.csv")
    global lexicon
    lexicon = True
    return pd.read_csv("./backend/data/my_data/clean_lexicon.csv", sep=';')


def import_tatoeba():
    """Import and return the tatoeba data (multiple choice)."""
    global lexicon
    lexicon = False
    return pd.read_csv("./backend/data/tatoeba/quiz_df.csv")


def retrieve_all_correct_answers(sentenceID):
    """Given a sentence ID, retrieve and return all other correct answers."""
    possible_answers = []
    if lexicon:
        data = import_lexicon()
    elif not lexicon:
        data = import_tatoeba()
    data = data.loc[data['sentenceID'] == sentenceID]
    for _, row in data.iterrows():
        if row['lang'] == 'en':
            possible_answers.append(row['sentence_en'])
        elif row['lang'] == 'nl':
            possible_answers.append(row['sentence_nl'])
    return possible_answers


def select_quiz_words(difficulty, number_of_questions, mode):
    """Select words that will be quizzed.

    Create and return a small df of size (number_of_questions).
    Mode currently is used as proxy for sentence/word questions,
    will be changed in the future. Difficulty is not taken into
    account yet, also future work (see issue #14).
    """
    # TODO
    if mode == 'multiple choice':
        df = import_tatoeba()
    elif mode == 'open':
        df = import_lexicon()

    # difficulty conditionals
    if difficulty == 'easy':
        lower = max(55000, 0)  # should change
        upper = 60038
        mu, sigma = 59000, 1000  # mu should change

    elif difficulty == 'moderate':
        lower = max(50000, 0)  # should change
        upper = 60038
        mu, sigma = 56500, 2000  # mu should change

    elif difficulty == 'difficult':
        lower = 0  # should change
        upper = 60038
        mu, sigma = 50000, 3000  # mu should change

    X = stats.truncnorm(
        a=(lower - mu) / sigma, b=(upper - mu) / sigma,
        loc=mu, scale=sigma)
    choice_list = list()
    print(X.rvs(size=1))
    print(int(X.rvs(1)))
    for i in range(number_of_questions):
        if int(X.rvs(1)) not in choice_list:
            choice_list.append(int(X.rvs(1)))

    df.sort_values(by='sentence_ease', ascending=True, inplace=True)
    chosen_words_df = df.iloc[choice_list]
    print(chosen_words_df)
    return chosen_words_df


def check_answers(given_answer, quiz_df, sentenceID):
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


def generate_answer_options(questionID):
    """Generates three incorrect answer options for multiple choice questions.

    In case of multiple choice questions, three incorrect options have to be selected.
    With just questionID, the first answer of all_correct_answers is taken (fewer args passed),
    and three random numbers are chosen for the incorrect options. Theoretically, if a question
    has multiple correct translations in the database, multiple options could be correct. However,
    as evaluation takes this into account, it will also be evaluated correctly, and no tricky
    edge case mitigation should be done to combat this unlikely event.
    Return both the already shuffled list with 4 answer options and the index of a correct one.
    """
    multiple_choice_options = []

    all_correct_answers = retrieve_all_correct_answers(questionID)
    multiple_choice_options.append(all_correct_answers[0])

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
    index = [multiple_choice_options.index(x) for x in multiple_choice_options if x in all_correct_answers][0]
    return multiple_choice_options, index


def update_dataframe():
    """Stores the quiz (meta)data to the appropriate locations. To be implemented."""
    pass
