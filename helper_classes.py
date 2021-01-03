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


# miss create_quiz die dan df maakt met
# | sentenceID | sentence_pl | correct_answers (including index) |
