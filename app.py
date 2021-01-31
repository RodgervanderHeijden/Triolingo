from flask import Flask, render_template, request, url_for, redirect
from helper_functions import after_quiz, convert_answer, worker
from helper_classes import User, Quiz, Question
import threading

triolingo_app = Flask(__name__)
current_user = User(name="Rodger")
global current_quiz


@triolingo_app.route("/")
def homepage():
    """Homepage. Can use some visual shabam, but works."""
    return render_template("homepage.html")


@triolingo_app.route("/settings", methods=["GET"])
def select_settings():
    """Form to select desired settings.

    Quite standard page to select settings.
    Potential to add a post-method, delete the action on the form,
    and an if-statement here with redirect to confirm_settings, no prio though."""
    return render_template("select_quiz_settings.html")


@triolingo_app.route('/quiz_confirmation', methods=["POST"])
def confirm_quiz_settings():
    """Confirm quiz settings and reroute to quiz.

    A page to confirm the selected quiz settings (from form of settings page).
    Initially required to solve the issue of having two forms in the quiz page,
    though not required anymore because of classes. However, pre-quiz an overview
    of the to-be-quizzed questions may still be displayed, and thus this page for
    now remains."""
    global current_quiz
    try: # If after a quiz the "repeat with same settings" button is chosen, no args will be passed (ie NoneType)
        current_quiz = Quiz(current_user,
                            difficulty=request.form.get('difficulty'),
                            no_questions=request.form.get('amount'),
                            mode=request.form.get("mode"))
    except TypeError:
        difficulty = current_quiz.difficulty
        no_questions = current_quiz.no_questions
        mode = current_quiz.mode
        current_quiz = Quiz(current_user,
                            difficulty=difficulty,
                            no_questions=no_questions,
                            mode=mode)
    current_quiz.create_quiz_df()
    return render_template("quiz_confirmation.html", difficulty=current_quiz.difficulty,
                           questions=current_quiz.no_questions, mode=current_quiz.mode)


@triolingo_app.route("/quiz/", methods=["POST"])
def quiz_page():
    """The quiz page.

    The beefy page where the quiz actually occurs. Takes in three args in URL.
    While the number of questions hasn't been reached, it goes in the loop, otherwise redirect.
    The loop has two conditions; either no answer has been given and thus a question will be displayed,
    or an answer has been given, and thus a question feedback page will be displayed."""
    given_answer = request.form.get('text', None)
    from_feedback_page = request.form.get('from_feedback_page', None)

    if (request.referrer[-18:] == '/quiz_confirmation') or (from_feedback_page is not None):
        global current_question
        current_question = Question(current_quiz)

    event = threading.Event()
    while current_quiz.correct < current_quiz.no_questions:
        sentenceID = int(current_quiz.sentenceIDs[current_quiz.current_question_no])
        # Two options exist:
        # A. the previous page is the settings, and thus you want to show a question
        # B. the previous page is the screen after an answer has been given, and thus now you want a new question
        if (request.referrer[-18:] == '/quiz_confirmation') or (from_feedback_page is not None):
            current_question.set_sentenceID(sentenceID)
            current_question.set_question_sentence(sentenceID)

            thread = threading.Thread(target=worker, args=(event, current_question.question_sentence))
            thread.start()

            if current_quiz.mode == 'multiple choice':
                current_question.generate_answer_options()
                return render_template("do_quiz.html", mode=current_quiz.mode,
                                       current_word=current_question.question_sentence, answer=given_answer,
                                       answer_option_1=current_question.answer_options[0],
                                       answer_option_2=current_question.answer_options[1],
                                       answer_option_3=current_question.answer_options[2],
                                       answer_option_4=current_question.answer_options[3])
            elif current_quiz.mode == 'open': # Is this truly open? Chekc whether this still works
                return render_template("do_quiz.html", mode=current_quiz.mode,
                                       current_word=current_question.question_sentence, answer=given_answer)

        # If a new answer is given (so not None), you now want a confirmation/feedback screen to be rendered.
        elif given_answer is not None:
            url = request.referrer
            if given_answer.lower() in ['a', 'b', 'c', 'd', '1', '2', '3', '4']:
                converted_answer = convert_answer(given_answer)
                is_correct = bool(current_question.correct_index == converted_answer)
                given_answer = current_question.answer_options[converted_answer]
            else:
                is_correct = current_question.check_answers(given_answer)

            current_question.add_to_quiz_results(given_answer, is_correct,)
            previous_question_no = current_quiz.current_question_no
            # If correct: quiz the next question
            if is_correct:
                current_quiz.correct += 1
                current_quiz.current_question_no += 1
            # If incorrect, quiz the same question.
            else:
                # Don't update anything
                current_quiz.incorrect += 1

            previous_question_ID = current_quiz.sentenceIDs[previous_question_no]
            current_question.set_sentenceID(previous_question_ID)
            previous_question = current_question.question_sentence
            return render_template("answer_feedback.html", given_answer=given_answer,
                                   previous_question=previous_question, url=url,
                                   is_correct=is_correct, correct_answer=current_question.correct_answers[0])

    return redirect(url_for("show_quiz_data"))


@triolingo_app.route("/after_quiz/", methods=["GET", "POST"])
def show_quiz_data():
    """Post-quiz diagnostics. Render df of quiz, update personal sentence ease and language proficiency."""
    after_quiz(current_user, current_quiz)
    render_df = current_quiz.quiz_results[['Question', 'Given answer', 'correct']]
    render_df.columns = ['Polish sentence', 'Your answer', 'Correct?']
    quiz_results_html = [render_df.to_html(index=False, classes='data')]
    return render_template("after_quiz.html", difficulty=current_quiz.difficulty,
                           no_questions=current_quiz.no_questions, mode=current_quiz.mode,
                           quiz_df=quiz_results_html)


@triolingo_app.route("/about")
def about():
    """Basic about page."""
    return render_template("about_triolingo.html")


@triolingo_app.route("/contact")
def contact():
    """Basic about page."""
    return render_template("contact.html")


if __name__ == '__main__':
    triolingo_app.run()
