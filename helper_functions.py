import string
from databases import quiz_logs, personal_ease
from gtts import gTTS
from random import randint
import os
import helper_classes

global previous_quiz

def create_quiz_object_with_settings(current_user, request):
    """Creates the quiz instance with the parameters the user has selected in his request."""
    if request.form.get("difficulty") is not None:  # If new quiz settings are selected (= not "repeat with same settings" after quiz)
        current_quiz = helper_classes.Quiz(current_user,
                            difficulty=request.form.get('difficulty'),
                            no_questions=request.form.get('amount'),
                            mode=request.form.get("mode"))
    else:
        global previous_quiz
        current_quiz = helper_classes.Quiz(current_user,
                                           difficulty=previous_quiz.difficulty,
                                           no_questions=previous_quiz.no_questions,
                                           mode=previous_quiz.mode)
    return current_quiz


def initialize_quiz(current_quiz):
    """Creates a quiz instance by first retrieving the quiz settings from the request,
    then creating the sampling distribution, then doing the sampling and getting the sentenceIDs."""
    # current_quiz = initialize_quiz_settings(current_user, request)
    distribution_params = current_quiz.calculate_distribution_parameters()
    chosen_indices = current_quiz.draw_words_from_chosen_distribution(distribution_params)
    current_quiz.retrieve_sentences_from_index(chosen_indices)


def generate_store_tts_audio(sentence):
    tts = gTTS(text=sentence, lang='pl', slow=False)
    r = randint(1,20000000)
    audio_file = 'audio' + str(r) + '.mp3'
    full_url = './static/' + audio_file
    tts.save(full_url) # save as mp3

    tts_slow = gTTS(text=sentence, lang='pl', slow=True)
    audio_file_2 = 'audio' + str(r+1) + '.mp3'
    full_url_2 = './static/' + audio_file_2
    tts_slow.save(full_url_2) # save as mp3
    return full_url, full_url_2


# Import the dataframe with all sentences
# TODO: change this to include the entire corpus of CLARIN
# see: http://clarin-pl.eu/en/home-page/
# see: http://nkjp.pl/index.php?page=14&lang=1
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


def after_quiz(user, current_quiz):
    """Method to call after quiz has finished. Write results, calculate new scores."""
    # Delete all mp3 files after the quiz.
    files_in_dir = os.listdir('./static')
    filtered_files = [file for file in files_in_dir if file.endswith(".mp3")]
    for file in filtered_files:
        path_to_file = os.path.join('./static', file)
        os.remove(path_to_file)

    global previous_quiz
    previous_quiz = helper_classes.Quiz(user.name,
                                        current_quiz.difficulty,
                                        current_quiz.no_questions,
                                        current_quiz.mode)

    error = calculate_error(current_quiz)
    quiz_logs.add_new_quiz(current_quiz)
    user.update_user_data(error, current_quiz.difficulty)
    personal_ease.update_personal_sentence_ease(current_quiz.quiz_results)


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
