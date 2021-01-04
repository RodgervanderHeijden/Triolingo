import pandas as pd
import scipy.stats as stats
import numpy as np


class User:
    def __init__(self,
                 language_proficiency,
                 name="Rodger",
                 ):
        self.language_proficiency = language_proficiency
        self.name = name,

        self.lr_easy = 1
        self.lr_moderate = 1
        self.lr_difficult = 1

        # len(database_backlog_of_quizzes)
        self.quizID = 1

    def update_language_proficiency(self, error):
        self.language_proficiency = self.language_proficiency * (1 + error * 0.1)

    def update_personal_learning_rate(self, difficulty_setting, error):
        if difficulty_setting == "easy":
            self.lr_easy = self.lr_easy * (self.lr_easy * (1 + 0.1 * error))
        elif difficulty_setting == "moderate":
            self.lr_moderate = self.lr_moderate * (self.lr_moderate * (1 + 0.1 * error))
        elif difficulty_setting == "difficult":
            self.lr_difficult = self.lr_difficult * (self.lr_difficult * (1 + 0.1 * error))
        else:
            return AssertionError


class Quiz:
    def __init__(self,
                 user,
                 difficulty="easy",
                 no_questions=int(10),
                 mode="multiple choice",
                 ):
        # self.language_proficiency = language_proficiency
        self.user = user
        self.difficulty = difficulty
        self.no_questions = int(no_questions)
        self.current_question_no = 0
        self.mode = mode
        self.quizzed_questions = None
        self.correct = 0
        self.incorrect = 0
        self.quiz_results = pd.DataFrame(columns=['sentenceID', 'Question', 'Given answer', 'correct'])

    def create_quiz_df(self):
        # Return lower bound, upper bound, mu and sigma in that order
        lower, upper = max(0, 0), 60039
        if self.difficulty == "easy":
            mu, sigma = self.user.language_proficiency * 60039 * self.user.lr_easy * 0.01, 200
        elif self.difficulty == "moderate":
            mu, sigma = self.user.language_proficiency * 60039 * self.user.lr_moderate * 0.05, 2000
        elif self.difficulty == "difficult":
            mu, sigma = self.user.language_proficiency * 60039 * self.user.lr_difficult * 0.10, 3000
        X = stats.truncnorm(
            a=(lower - mu) / sigma, b=(upper - mu) / sigma,
            loc=mu, scale=sigma)
        choice_list = list()

        while len(choice_list) < self.no_questions:
            single_sample = int(X.rvs(1))
            if single_sample not in choice_list:
                choice_list.append(single_sample)

        all_translated_sentences = pd.read_csv("./backend/data/tatoeba/quiz_df.csv", sep=',')
        self.quizzed_questions = all_translated_sentences.iloc[choice_list]


# Wss beter om question als parameter "sentenceID" te geven, en Quiz een method van "get_next_sentenceID".
class Question:
    def __init__(self, current_quiz):
        self.current_quiz = current_quiz
        self.question_sentence = ""
        self.correct_answers = []
        self.incorrect_answers = []
        self.answer_options = []
        self.sentenceID = ""
        self.correct_index = int()

    def set_sentenceID(self, sentenceID):
        self.sentenceID = sentenceID

    def set_question_sentence(self):
        entire_database = pd.read_csv("./backend/data/tatoeba/quiz_df.csv", sep=',')
        self.question_sentence = entire_database.loc[entire_database['sentenceID'] == self.sentenceID].iloc[0][
            'sentence_pl']

    def generate_correct_answers(self):
        entire_database = pd.read_csv("./backend/data/tatoeba/quiz_df.csv", sep=',')
        correct_rows = entire_database.loc[entire_database['sentenceID'] == self.sentenceID]
        possible_answers = []
        for _, row in correct_rows.iterrows():
            if row['lang'] == 'en':
                possible_answers.append(row['sentence_en'])
            elif row['lang'] == 'nl':
                possible_answers.append(row['sentence_nl'])
        self.correct_answers = possible_answers

    def generate_incorrect_answers(self):
        entire_database = pd.read_csv("./backend/data/tatoeba/quiz_df.csv", sep=',')
        three_random_numbers = np.random.choice(a=range(len(entire_database)), size=3,
                                                replace=False)
        incorrect_answer_options = []
        for _, row in entire_database.iloc[three_random_numbers].iterrows():
            if row['lang'] == 'en':
                incorrect_answer_options.append(row['sentence_en'])
            elif row['lang'] == 'nl':
                incorrect_answer_options.append(row['sentence_nl'])
        self.incorrect_answers = incorrect_answer_options

    def generate_answer_options(self):
        """Generates three incorrect answer options for multiple choice questions.

            In case of multiple choice questions, three incorrect options have to be selected.
            With just questionID, the first answer of all_correct_answers is taken (fewer args passed),
            and three random numbers are chosen for the incorrect options. Theoretically, if a question
            has multiple correct translations in the database, multiple options could be correct. However,
            as evaluation takes this into account, it will also be evaluated correctly, and no tricky
            edge case mitigation should be done to combat this unlikely event.
            Return both the already shuffled list with 4 answer options and the index of a correct one."""
        self.generate_correct_answers()
        self.generate_incorrect_answers()

        multiple_choice_options = [self.correct_answers[0]]
        for incorrect_answer in self.incorrect_answers:
            multiple_choice_options.append(incorrect_answer)
        np.random.shuffle(multiple_choice_options)
        index = [multiple_choice_options.index(x) for x in multiple_choice_options if x in self.correct_answers][0]
        self.correct_index = index
        self.answer_options = multiple_choice_options

    def check_answers(self):
        if True:
            self.current_quiz.correct += 1
            self.current_quiz.current_question_no += 1
        elif False:
            self.current_quiz.false += 1

    # After each question, add sentence_pl, given answer and correct Bool to quiz results.
    # Quiz results will be called in after_quiz
    def add_to_quiz_results(self, given_answer, is_correct):
        self.current_quiz.quiz_results = self.current_quiz.quiz_results.append({'sentenceID': self.sentenceID,
                                                                                'Question': self.question_sentence,
                                                                                'Given answer': given_answer,
                                                                                'correct': is_correct},
                                                                               ignore_index=True
                                                                               )

    # Na elke vraag de update aanvragen (in feedback scherm), diff = Quiz.diff
    def update_personal_sentence_ease(self, is_correct, difficulty):
        pass
