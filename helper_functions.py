import os
from random import randint

from gtts import gTTS

import helper_classes
from databases import quiz_logs, personal_ease
from typing import Type, Tuple

global previous_quiz


def create_quiz_object_with_settings(empty_quiz_instance: Type[helper_classes.Quiz], request) -> None:
    """Takes the empty quiz instance with the parameters the user has selected in his request - if any."""
    if request.form.get(
            "difficulty") is not None:  # If new quiz settings are selected (= not "repeat with same settings" after quiz)
        empty_quiz_instance.set_quiz_params(difficulty=request.form.get('difficulty'),
                                            no_questions=request.form.get('amount'),
                                            mode=request.form.get("mode"))
    else:  # If after a quiz the "repeat with same settings" button is used, there's an empty request
        global previous_quiz
        empty_quiz_instance.set_quiz_params(difficulty=previous_quiz.difficulty,
                                            no_questions=previous_quiz.no_questions,
                                            mode=previous_quiz.mode)


def initialize_quiz_questions(current_quiz: Type[helper_classes.Quiz]) -> None:
    """Creates a quiz instance by first retrieving the quiz settings from the request,
    then creating the sampling distribution, then doing the sampling and getting the sentenceIDs."""
    # current_quiz = initialize_quiz_settings(current_user, request)
    distribution_params = current_quiz.calculate_distribution_parameters()
    chosen_indices = current_quiz.draw_words_from_chosen_distribution(distribution_params)
    current_quiz.retrieve_sentences_from_index(chosen_indices)


def create_tts_audio(sentence: str, slow: bool, random_number: int) -> str:
    audio_file_name = 'audio' + str(random_number) + '.mp3'
    full_file_path = './static/' + audio_file_name
    tts = gTTS(text=sentence, lang='pl', slow=slow)
    tts.save(full_file_path)  # save as mp3
    return full_file_path


def generate_store_tts_audio(sentence: str) -> Tuple[str, str]:
    r = randint(1, 20000000)
    normal_speed_file_path = create_tts_audio(sentence, slow=False, random_number=r)
    slow_speed_file_path = create_tts_audio(sentence, slow=True, random_number=r + 1)
    return normal_speed_file_path, slow_speed_file_path


# Import the dataframe with all sentences
# TODO: change this to include the entire corpus of CLARIN
# see: http://clarin-pl.eu/en/home-page/
# see: http://nkjp.pl/index.php?page=14&lang=1
def convert_str_answer_to_int(given_answer: str) -> int:
    # Is answer was given as letter, convert to numerical
    if given_answer == 'a':
        given_answer = 1
    elif given_answer == 'b':
        given_answer = 2
    elif given_answer == 'c':
        given_answer = 3
    elif given_answer == 'd':
        given_answer = 4
    return int(given_answer)


def convert_given_answer_to_index(given_answer: str) -> int:
    """If the given answer is a str, converts it to an int. Subtracts one to use it as index."""
    if given_answer in ['a', 'b', 'c', 'd']:
        given_answer = convert_str_answer_to_int(given_answer)
    return int(given_answer) - 1


def expected_correct_ratio(difficulty: str) -> float:
    """Returns the expected ratio of correct questions."""
    if difficulty == "easy":
        return 0.8
    elif difficulty == "moderate":
        return 0.6
    elif difficulty == "difficult":
        return 0.3


def calculate_error(current_quiz: Type[helper_classes.Quiz]) -> float:
    y_hat = expected_correct_ratio(current_quiz.difficulty)
    score = current_quiz.correct / (current_quiz.correct + current_quiz.incorrect)
    error = (score - y_hat)
    return error


def delete_audio_files():
    # Delete all mp3 files after the quiz.
    files_in_dir = os.listdir('./static')
    filtered_files = [file for file in files_in_dir if file.endswith(".mp3")]
    for file in filtered_files:
        path_to_file = os.path.join('./static', file)
        os.remove(path_to_file)


def after_quiz(user: Type[helper_classes.User], current_quiz: Type[helper_classes.Quiz]) -> Type[helper_classes.Quiz]:
    """Method to call after quiz has finished. Write results, calculate new scores."""
    delete_audio_files()

    error = calculate_error(current_quiz)
    quiz_logs.add_new_quiz(current_quiz)
    user.update_user_data(error, current_quiz.difficulty)
    personal_ease.update_personal_sentence_ease(current_quiz.quiz_results)
    # Once all info regarding the completed quiz has been updated, a 'new' quiz previous_quiz gets made
    # that stores all information.
    global previous_quiz
    previous_quiz = current_quiz
    return previous_quiz

# # Functional in isolation, no implementation done.
# import smtplib, ssl
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# def update_inactivity_mail():
#     """Is fully functioning (though"""
#     sender_email = "redacted"
#     receiver_email = "redacted"
#     password = input("Type your password and press enter:")
#
#     message = MIMEMultipart("Inactivity")
#     message["Subject"] = "You've been inactive on Triolingo!"
#     message["From"] = sender_email
#     message["To"] = receiver_email
#
#     # Create the plain-text and HTML version of your message
#     text = """\
#     Hi,
#     According to our logs you've been slacking!
#     Get started with your Polish by clicking the button below:
#     Go to Triolingo!"""
#     html = """\
#     <html>
#         <body>
#             <h2>Hi,</h2>
#             <p>According to our logs you've been slacking!<br>
#             Get started with your Polish by clicking the button below:
#             </p>
#             <form action="127.0.0.1:5000">
#                 <input type="submit" value="Go to Triolingo!" />
#             </form>
#         </body>
#     </html>
#     """
#
#     # Turn these into plain/html MIMEText objects
#     part1 = MIMEText(text, "plain")
#     part2 = MIMEText(html, "html")
#
#     # Add HTML/plain-text parts to MIMEMultipart message
#     # The email client will try to render the last part first
#     message.attach(part1)
#     message.attach(part2)
#
#     # Create secure connection with server and send email
#     context = ssl.create_default_context()
#     with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
#         server.login(sender_email, password)
#         server.sendmail(
#             sender_email, receiver_email, message.as_string()
#         )
