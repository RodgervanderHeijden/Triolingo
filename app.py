from flask import Flask, render_template, request, url_for, redirect
from helper_functions import select_quiz_words, check_answers, generate_answer_options, after_quiz
from helper_functions import convert_answer
import pandas as pd

app = Flask(__name__)
# temp variables, currently used as globals but to be rewritten as cookies or a class
current_question_no = 0
answer_options = []
index = 0
quiz_df = pd.DataFrame()
quiz_results = pd.DataFrame(columns=['sentenceID', 'Question', 'Given answer', 'correct'])


@app.route('/quiz_confirmation', methods=["POST"])
def confirm_quiz_settings():
    """Confirm quiz settings and reroute to quiz with arguments in url.

    A page to confirm the selected quiz settings (from form of settings page).
    Initially required to solve the issue of having two forms in the quiz page,
    though it might be mitigated by using globals, url args and even sessions.
    For now, it works and it's fine.
    Current_question_no has to be set to 0, otherwise the second quiz does not work."""
    no_questions = int(request.form.get("amount"))
    difficulty = request.form.get('difficulty')
    mode = request.form.get("mode")
    global current_question_no
    current_question_no = 0
    global quiz_results
    quiz_results = pd.DataFrame(columns=['sentenceID', 'Question', 'Given answer', 'correct'])
    global quiz_df
    quiz_df = select_quiz_words(difficulty, no_questions, mode)
    return render_template("quiz_confirmation.html", difficulty=difficulty,
                           questions=no_questions, mode=mode)


@app.route("/quiz/<difficulty>/<no_questions>/<mode>/", methods=["POST"])
def quiz_page(difficulty="easy", no_questions=10, mode='Sentence'):
    """The quiz page.

    The beefy page where the quiz actually occurs. Takes in three args in URL.
    While the number of questions hasn't been reached, it goes in the loop, otherwise redirect.
    The loop has two conditions; the first one is when the form does not (yet) have a text,
    i.e. no answer has been given yet, i.e. the user arrives from quiz_setting_confirmation.
    The quiz subdf get decided there and written to global."""
    # Get from URL
    no_questions = int(no_questions)
    given_answer = request.form.get('text', None)
    from_feedback_page = request.form.get('from_feedback_page', None)

    # Upon first visit of the route, no answer has yet been given
    # Here a to be quizzed sub df gets selected and returned
    global current_question_no
    global quiz_results
    while sum(quiz_results['correct']) < no_questions:

        if request.referrer[-18:] == '/quiz_confirmation':
            current_question = quiz_df.iloc[current_question_no]['sentence_pl']
            sentenceID = quiz_df.iloc[current_question_no]['sentenceID']
            quiz_df_html = [quiz_df.to_html(classes='data')]

            if mode == 'multiple choice':
                global answer_options, index
                answer_options, index = generate_answer_options(sentenceID)
                return render_template("do_quiz.html", quiz_df=quiz_df_html, mode=mode, current_word=current_question,
                                       answer_option_1=answer_options[0], answer_option_2=answer_options[1],
                                       answer_option_3=answer_options[2], answer_option_4=answer_options[3])
            elif mode == 'open':
                return render_template("do_quiz.html", quiz_df=quiz_df_html, mode=mode, current_word=current_question,
                                       answer=given_answer)

        else:
            # Two options exist:
            # A. the previous page is the quiz, and thus the request holds an answer
            # B. the previous page is the screen after an answer has been given, and thus holds no new answer.

            # If a new answer is given (so not None), you now want a confirmation/feedback screen to be rendered.
            if given_answer is not None:
                url = request.referrer

                sentenceID = quiz_df.iloc[current_question_no]['sentenceID']
                if given_answer.lower() in ['a', 'b', 'c', 'd', '1', '2', '3', '4']:
                    converted_answer = convert_answer(given_answer)
                    is_correct = bool(index == converted_answer)
                    given_answer = answer_options[converted_answer]

                else:
                    is_correct = check_answers(given_answer, quiz_df, sentenceID)

                # Update current question and add it to the quiz results df
                current_question = quiz_df.iloc[current_question_no]['sentence_pl']
                quiz_results = quiz_results.append({'sentenceID': sentenceID,
                                                    'Question': current_question,
                                                    'Given answer': given_answer,
                                                    'correct': is_correct},
                                                   ignore_index=True)
                # If correct: quiz the next question
                if is_correct:
                    # Update index and generate a new sentenceID
                    previous_question_no = current_question_no
                    current_question_no = current_question_no + 1

                # If incorrect, quiz the same question.
                else:
                    # Don't update anything
                    previous_question_no = current_question_no

                previous_question = quiz_df.iloc[previous_question_no]['sentence_pl']
                return render_template("answer_feedback.html", given_answer=given_answer,
                                       current_question=previous_question, url=url,
                                       is_correct=is_correct)

            elif (from_feedback_page is not None) & (given_answer is None):
                quiz_df_html = [quiz_df.to_html(classes='data')]
                current_question = quiz_df.iloc[current_question_no]['sentence_pl']
                if mode == 'multiple choice':
                    sentenceID = quiz_df.iloc[current_question_no]['sentenceID']
                    answer_options, index = generate_answer_options(sentenceID)

                    return render_template("do_quiz.html", quiz_df=quiz_df_html, mode=mode,
                                           current_word=current_question, answer=given_answer,
                                           answer_option_1=answer_options[0], answer_option_2=answer_options[1],
                                           answer_option_3=answer_options[2], answer_option_4=answer_options[3], )
                elif mode == 'open':
                    return render_template("do_quiz.html", quiz_df=quiz_df_html, mode=mode,
                                           current_word=current_question, answer=given_answer, )

    return redirect(url_for("show_quiz_data", difficulty=difficulty, no_questions=no_questions, mode=mode))


@app.route("/after_quiz/<difficulty>/<no_questions>/<mode>/", methods=["GET", "POST"])
def show_quiz_data(difficulty, no_questions, mode):
    """Post-quiz diagnostics. Render df of quiz, update personal sentence ease and language proficiency."""

    global quiz_results
    after_quiz(quiz_results, difficulty)

    #global quiz_results
    quiz_results_html = [quiz_results.to_html(classes='data')]
    return render_template("after_quiz.html", difficulty=difficulty, no_questions=no_questions, mode=mode,
                           quiz_df=quiz_results_html)


@app.route("/settings", methods=["GET"])
def select_settings():
    """Form to select desired settings.

    Quite standard page to select settings.
    Potential to add a post-method, delete the action on the form,
    and an if-statement here with redirect to confirm_settings, no prio though."""
    return render_template("select_quiz_settings.html")


@app.route("/")
def homepage():
    """Homepage. Can use some visual shabam, but works."""
    return render_template("homepage.html")


@app.route("/about")
def about():
    """Basic about page."""
    return render_template("about_triolingo.html")


@app.route("/contact")
def contact():
    """Basic about page."""
    return render_template("contact.html")


if __name__ == '__main__':
    app.run()
