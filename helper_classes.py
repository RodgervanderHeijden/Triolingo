import pandas as pd
import scipy.stats as stats
import numpy as np
import string
from databases import users, personal_ease


class User:
    def __init__(self,
                 name="Rodger",
                 ):
        self.name = name
        user_data = users.return_user_data(name)
        print(user_data)

        self.name = str(user_data['user_name'].values[0])
        self.language_proficiency = float(user_data['language_proficiency'])
        self.lr_easy = float(user_data['lr_easy'])
        self.lr_moderate = float(user_data['lr_moderate'])
        self.lr_difficult = float(user_data['lr_difficult'])

    def update_user_data(self, error, quiz_difficulty):
        """Update the language proficiency and learning rates of the user."""
        updated_values = users.update_user_info(self, error, quiz_difficulty)
        self.language_proficiency = float(updated_values['language_proficiency'])
        self.lr_easy = float(updated_values['lr_easy'])
        self.lr_moderate = float(updated_values['lr_moderate'])
        self.lr_difficult = float(updated_values['lr_difficult'])


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
        self.sentenceIDs = []

    def calculate_distribution_parameters(self):
        """Create a normal-like curve with truncation for weighted question selection."""
        # Return lower bound, upper bound, mu and sigma in that order
        lower, upper = max(0, 0), 60039
        if self.difficulty == "easy":
            mu, sigma = self.user.language_proficiency * 60039 * self.user.lr_easy * 0.0001, 200
        elif self.difficulty == "moderate":
            mu, sigma = self.user.language_proficiency * 60039 * self.user.lr_moderate * 0.0005, 2000
        elif self.difficulty == "difficult":
            mu, sigma = self.user.language_proficiency * 60039 * self.user.lr_difficult * 0.0010, 3000

        return stats.truncnorm(
            a=(lower - mu) / sigma, b=(upper - mu) / sigma,
            loc=mu, scale=sigma)

    def draw_words_from_chosen_distribution(self, distribution_params):
        """Initializes an empty list and draws based on the generated distribution parameters.
        If the selected index (by coincidence) is drawn again, a new draw takes place."""
        # calculated_distribution_parameters = self.calculate_distribution_parameters()
        choice_list = list()
        while len(choice_list) < self.no_questions:
            single_sample = int(distribution_params.rvs(1))
            if single_sample not in choice_list:
                choice_list.append(single_sample)
        return choice_list

    def retrieve_sentences_from_index(self, choice_list):
        """Based on the selected indices, retrieves the associated sentences and sets it in self"""
        # choice_list = self.draw_words_from_chosen_distribution()
        sentenceIDs = personal_ease.return_chosen_sentenceIDs(choice_list).values
        self.sentenceIDs = sentenceIDs


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

    def set_question_sentence(self, sentenceID):
        self.question_sentence = personal_ease.get_question_sentence(sentenceID)
        return self.question_sentence

    def generate_answer_options(self):
        """Generates three incorrect answer options for multiple choice questions.

            In case of multiple choice questions, three incorrect options have to be selected.
            With just questionID, the first answer of all_correct_answers is taken (fewer args passed),
            and three random numbers are chosen for the incorrect options. Theoretically, if a question
            has multiple correct translations in the database, multiple options could be correct. However,
            as evaluation takes this into account, it will also be evaluated correctly, and no tricky
            edge case mitigation should be done to combat this unlikely event.
            Return both the already shuffled list with 4 answer options and the index of a correct one."""
        self.correct_answers, incorrect_answers = personal_ease.get_answer_options(self.sentenceID)

        multiple_choice_options = [self.correct_answers[0]]
        for incorrect_answer in incorrect_answers:
            multiple_choice_options.append(incorrect_answer)
        np.random.shuffle(multiple_choice_options)
        index = [multiple_choice_options.index(x) for x in multiple_choice_options if x in self.correct_answers][0]
        self.correct_index = index
        self.answer_options = multiple_choice_options

    def check_answers(self, given_answer):
        remove_punctuation = str.maketrans("", "", string.punctuation)
        cleaned_given_answer = given_answer.lower().translate(remove_punctuation)
        cleaned_correct_answers = []
        for possible_answer in self.correct_answers:
            # Using the same remove_punctuation translation as defined above
            cleaned_answer = possible_answer.lower().translate(remove_punctuation)
            cleaned_correct_answers.append(cleaned_answer)
        return cleaned_given_answer in cleaned_correct_answers

    # After each question, add sentence_pl, given answer and correct Bool to quiz results.
    # Quiz results will be called in after_quiz
    def add_to_quiz_results(self, given_answer, is_correct):
        """Add metadata to quiz_results dataframe, a dataframe during a quiz. Will be stored in db on finish."""
        self.current_quiz.quiz_results = self.current_quiz.quiz_results.append({'sentenceID': self.sentenceID,
                                                                                'Question': self.question_sentence,
                                                                                'Given answer': given_answer,
                                                                                'correct': is_correct},
                                                                               ignore_index=True
                                                                               )
