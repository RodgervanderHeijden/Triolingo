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
    global lexicon
    lexicon = True
    return pd.read_csv("./backend/data/my_data/clean_lexicon.csv", sep=';')


def import_tatoeba():
    """Import and return the tatoeba data (multiple choice)."""
    global lexicon
    lexicon = False
    return pd.read_csv("./backend/data/tatoeba/quiz_df.csv").sort_values(by=['sentence_ease'], ascending=False)


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


def generate_answer_options(questionID):
    """Generates three incorrect answer options for multiple choice questions.

    In case of multiple choice questions, three incorrect options have to be selected.
    With just questionID, the first answer of all_correct_answers is taken (fewer args passed),
    and three random numbers are chosen for the incorrect options. Theoretically, if a question
    has multiple correct translations in the database, multiple options could be correct. However,
    as evaluation takes this into account, it will also be evaluated correctly, and no tricky
    edge case mitigation should be done to combat this unlikely event.
    Return both the already shuffled list with 4 answer options and the index of a correct one."""
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


def select_quiz_words(difficulty, number_of_questions, mode):
    """Select words that will be quizzed.

    Create and return a small df of size (number_of_questions).
    Mode currently is used as proxy for sentence/word questions,
    will be changed in the future."""
    # TODO
    if mode == 'multiple choice':
        df = import_tatoeba()
    elif mode == 'open':
        df = import_lexicon()

    # A percentage along the df-length for where the mean of the distribution should lie
    # More good questions thus should increase these values, and the proportion of the df
    # that is considered known. The three etas should be linked at some stage, to ensure
    # that the easy questions (after a lot of practicing) don't become more difficult than
    # the moderate ones etc
    easy_eta = 0.01
    moderate_eta = 0.05
    difficult_eta = 0.10
    # difficulty conditionals
    if difficulty == 'easy':
        lower = max(0, 0)  # should change (one should allow movement, other should stay 0 for certainty)
        upper = len(df)-1
        mu, sigma = easy_eta*len(df), 200  # mu should change

    elif difficulty == 'moderate':
        lower = max(0, 0)  # should change
        upper = len(df)-1
        mu, sigma = moderate_eta*len(df), 2000  # mu should change

    elif difficulty == 'difficult':
        lower = max(0,0)  # should change
        upper = len(df)-1
        mu, sigma = difficult_eta*len(df), 3000  # mu should change

    X = stats.truncnorm(
        a=(lower - mu) / sigma, b=(upper - mu) / sigma,
        loc=mu, scale=sigma)
    choice_list = list()

    while len(choice_list) < number_of_questions:
        single_sample = int(X.rvs(1))
        if single_sample not in choice_list:
            choice_list.append(single_sample)

    chosen_words_df = df.iloc[choice_list]
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


def expected_correct_ratio(difficulty):
    """Returns the expected ratio of correct questions."""
    if difficulty == "easy":
        return 0.8
    elif difficulty == "moderate":
        return 0.6
    elif difficulty == "hard":
        return 0.3


def calculate_error(difficulty, quiz_list):
    y_hat = expected_correct_ratio(difficulty)
    score = sum(quiz_results[1])/len(quiz_results)
    error = (score-y_hat)
    print(error, score, y_hat)

    update_eta(error, quiz_list)




def update_eta(error, quiz_list):
    global eta
    eta = eta * (1 + error)
    mu = eta * 0.01 * 60000
    print(f"Here is the eta {eta} and mu {mu}")
    global sentence_scores

    for sentence_score in range(len(sentence_scores)):
        if quiz_list[sentence_score]:
            sentence_scores[sentence_score] = sentence_scores[sentence_score] * 1.20
        else:
            sentence_scores[sentence_score] = sentence_scores[sentence_score] * 0.80

    sentence_scores = sentence_scores
    print(sentence_scores)


def update_dataframe():
    """Stores the quiz (meta)data to the appropriate locations. To be implemented."""
    pass


def after_quiz():
    """Method to call after quiz has finished. Write results, calculate new scores."""
    update_eta()
    update_dataframe()