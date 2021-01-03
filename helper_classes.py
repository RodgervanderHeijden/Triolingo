import pandas as pd
import scipy.stats as stats


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
        self.mode = mode
        self.quizzed_questions = None
        self.correct = 0
        self.false = 0

    def create_quiz_df(self):
        # Return lower bound, upper bound, mu and sigma in that order
        lower, upper = max(0,0), 60039
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


class Question:
    def __init__(self, current_quiz, current_question_no):
        self.current_quiz = current_quiz
        self.current_question_no = current_question_no
        self.correct_answers = []
        self.sentenceID = ""

    def set_sentenceID(self, sentenceID):
        self.sentenceID = sentenceID

    def generate_correct_answers(self):
        entire_database = pd.read_csv("./backend/data/tatoeba/quiz_df.csv", sep=',')
        correct_rows = entire_database.loc[entire_database['sentenceID'] == self.sentenceID]
        print(correct_rows)
        possible_answers = []
        for _, row in correct_rows.iterrows():
            if row['lang'] == 'en':
                possible_answers.append(row['sentence_en'])
            elif row['lang'] == 'nl':
                possible_answers.append(row['sentence_nl'])
        self.correct_answers = possible_answers

    def check_answers(self):
        if True:
            self.current_quiz.correct += 1
            print(self.current_quiz.correct)
            self.current_question_no += 1
        elif False:
            self.current_quiz.false += 1
            print(self.current_quiz.correct)

    # After each question, add sentence_pl, given answer and correct Bool to quiz results.
    # Quiz results will be called in affter_quiz
    def add_to_quiz_results(self, sentenceID, given_answer):
        pass

    # Na elke vraag de update aanvragen (in feedback scherm), diff = Quiz.diff
    def update_personal_sentence_ease(self, is_correct, difficulty):
        pass

