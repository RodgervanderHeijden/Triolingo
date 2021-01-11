import pandas as pd
import string

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


def check_answers(given_answer, sentenceID, current_question):
    """Check whether the user-provided answer is correct.

    Given answer and the sentenceID, check whether it is correct.
    First use question_number (as index of quiz_df) to find matching
    sentenceID, then call retrieve_all_correct_answers for that ID.
    If the provided answer is in the list of possible answers, it is
    correct (True), otherwise not (False). Return result."""
    possible_answers = current_question.correct_answers
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


def calculate_error(current_quiz):
    y_hat = expected_correct_ratio(current_quiz.difficulty)
    score = current_quiz.correct/(current_quiz.correct + current_quiz.incorrect)
    error = (score-y_hat)
    return error

# Doesn't work yet.
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


def after_quiz(user, current_quiz):
    """Method to call after quiz has finished. Write results, calculate new scores."""
    error = calculate_error(current_quiz)
    user.update_language_proficiency(error)

    #update_dataframe(quiz_results)
