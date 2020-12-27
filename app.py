from flask import Flask, render_template, request, url_for, redirect, session
from helper_functions import select_quiz_words, check_answers, generate_answer_options
import random

app = Flask(__name__)

current_question_no = [0]


@app.route('/quiz_confirmation', methods=["POST"])
def confirm_quiz_settings():
    '''
        A page to confirm the selected quiz settings (from form of settings page).
        Initially required to solve the issue of having two forms in the quiz page,
        though it might be mitigated by using globals, url args and even sessions.
        For now, it works and it's fine.
        Current_question_no has to be set to 0, otherwise the second quiz does not work.
    '''
    questions = int(request.form.get("amount"))
    difficulty = request.form.get('difficulty')
    mode = request.form.get("mode")
    global current_question_no
    current_question_no = [0]
    return render_template("quiz_confirmation.html", difficulty=difficulty,
                           questions=questions, mode=mode)


@app.route("/quiz/<difficulty>/<no_questions>/<mode>/", methods=["POST"])
def quiz_page(difficulty="easy", no_questions=10, mode='Sentence'):
    '''
        The beefy page where the quiz actually occurs. Takes in three args in URL.
        While the number of questions hasn't been reached, it goes in the loop, otherwise redirect.
        The loop has two conditions; the first one is when the form does not (yet) have a text,
        i.e. no answer has been given yet, i.e. the user arrives from quiz_setting_confirmation.
        The quiz subdf get decided there and written to global.
    '''
    # Get from URL
    no_questions=int(no_questions)
    answer_bool = request.form.get('text', None)

    # Upon first visit of the route, no answer has yet been given
    # Here a to be quizzed sub df gets selected and returned
    while current_question_no[0] < no_questions-1:
        if (request.method == "POST") & (answer_bool is None):

            global quiz_df
            quiz_df = select_quiz_words(difficulty, no_questions, mode)
            current_question = quiz_df.iloc[current_question_no[0]]['sentence_pl']
            current_questionID = quiz_df.iloc[current_question_no[0]]['sentenceID']

            quiz_df_html = [quiz_df.to_html(classes='data')]

            if mode == 'multiple choice':
                correct_answer, incorrect_answers = generate_answer_options(current_questionID)
                answer_options = [x for x in incorrect_answers]
                answer_options.append(correct_answer)
                random.shuffle(answer_options)
                return render_template("do_quiz.html", difficulty=difficulty, no_questions=no_questions,
                                       quiz_df=quiz_df_html, mode=mode, current_word=current_question,
                                       answer_options=answer_options)
            elif mode == 'open':
                return render_template("do_quiz.html", difficulty=difficulty, no_questions=no_questions,
                                       quiz_df=quiz_df_html, mode=mode, current_word=current_question)

        else:
            sentenceID = quiz_df.iloc[current_question_no[0]]['sentenceID']

            is_correct = check_answers(answer_bool, quiz_df, current_question_no[0])
            # Update index
            current_question_no[0] = current_question_no[0] + 1
            current_question = quiz_df.iloc[current_question_no[0]]['sentence_pl']
            current_questionID = quiz_df.iloc[current_question_no[0]]['sentenceID']

            # TODO
            # check whether answer is correct
            # If correct: quiz the next question
            if is_correct:
                print("Correct")
            # If incorrect, quiz the same question.
            else:
                print("Incorrect!")

            quiz_df_html = [quiz_df.to_html(classes='data')]

            if mode == 'multiple choice':
                correct_answer, incorrect_answers = generate_answer_options(current_questionID)
                answer_options = [x for x in incorrect_answers]
                answer_options.append(correct_answer)
                random.shuffle(answer_options)
                return render_template("do_quiz.html", difficulty=difficulty, no_questions=no_questions,
                                       quiz_df=quiz_df_html, mode=mode, current_word=current_question,
                                       answer_options=answer_options, answer=answer_bool,)
            elif mode == 'open':
                return render_template("do_quiz.html", difficulty=difficulty, no_questions=no_questions,
                                       quiz_df=quiz_df_html, mode=mode, current_word=current_question, answer=answer_bool,)

    return redirect(url_for("show_quiz_data", difficulty=difficulty, no_questions=no_questions, mode=mode))


@app.route("/after_quiz/<difficulty>/<no_questions>/<mode>/", methods=["GET", "POST"])
def show_quiz_data(difficulty, no_questions, mode):
    '''
        With args in URL and global quiz_df shows the quizzed words and settings.
        Probably will be reworked to work with sessions, and requires some backend functionality still.
    '''

    # TODO
    def update_lexicon():
        pass

    quiz_df_html = [quiz_df.to_html(classes='data')]
    return render_template("after_quiz.html", difficulty=difficulty, no_questions=no_questions, mode=mode,
                           quiz_df=quiz_df_html)


@app.route("/settings", methods=["GET"])
def select_settings():
    '''
        Quite standard page to select settings.
        Potential to add a post-method, delete the action on the form,
        and an if-statement here with redirect to confirm_settings, no prio though.
        Some css shabam is desired, yet not necessary.
    '''
    return render_template("select_quiz_settings.html")


@app.route("/")
def index():
    '''
        Homepage. Can use some visual shabam, but works.
    '''
    return render_template("homepage.html")


@app.route("/about")
def about():
    '''
        Currently (mostly) populated with lorem ipsum, low prio to actually write about the project (for now).
    '''
    return render_template("about_triolingo.html")


if __name__ == '__main__':
    app.run(debug=True)
