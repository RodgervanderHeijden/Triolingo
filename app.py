from flask import Flask, render_template, request, url_for, redirect, flash
from helper_functions import import_lexicon, select_quiz_words, check_answers
import pandas as pd

app = Flask(__name__)

list_of_numbers = [1, 2, 4]
current_question = [0]


@app.route('/quiz_confirmation', methods=["POST"])
def confirm_quiz_settings():
    # De request hier komt van settings af
    # en bestaat dus uit mode en questions
    questions = int(request.form.get("amount"))
    print(questions+1)
    print(questions+1)
    if request.form.get("mode") == "Mastering words":
        difficulty = "mastery"
    elif request.form.get("mode") == "Mixture":
        difficulty = "mixed"
    elif request.form.get("mode") == "Learning new words":
        difficulty = "new"
    return render_template("quiz_confirmation.html", difficulty=difficulty,
                           questions=questions)


@app.route("/quiz/<difficulty>/<no_questions>/", methods=["POST"])
def quiz_page(difficulty="mastery", no_questions=10):
    print(request.form)
    # Get from URL
    no_questions=int(no_questions)
    answer_bool = request.form.get('text', None)

    # Upon first visit of the route, no answer has yet been given
    # Here a to be quizzed sub df gets selected and returned


    while current_question[0] < no_questions-1:
        print(current_question[0], no_questions)
        if (request.method == "POST") & (answer_bool is None):
            global quiz_df
            quiz_df = select_quiz_words(difficulty, no_questions)
            current_word = quiz_df.iloc[current_question[0]]['Polish']

            quiz_df_html = [quiz_df.to_html(classes='data')]
            return render_template("do_quiz.html", difficulty=difficulty, no_questions=no_questions,
                                   quiz_df=quiz_df_html, current_word=current_word)

        else:
            is_correct = check_answers(answer_bool, quiz_df, current_question[0])
            # Update index
            current_question[0] = current_question[0] + 1
            current_word = quiz_df.iloc[current_question[0]]['Polish'] # line two
            # TODO
            # check whether answer is correct
            if is_correct:
                print("Correct")
            else:
                print("Incorrect!")
            quiz_df_html = [quiz_df.to_html(classes='data')]
            return render_template("do_quiz.html", difficulty=difficulty, no_questions=no_questions,
                                   answer=answer_bool, current_word=current_word, quiz_df=quiz_df_html)

    return redirect(url_for("show_quiz_data", difficulty=difficulty, no_questions=no_questions))


# TODO: receive quiz data as argument
@app.route("/after_quiz/<difficulty>/<no_questions>/", methods=["GET", "POST"])
def show_quiz_data(difficulty, no_questions):

    # TODO
    def update_lexicon():
        pass

    return render_template("after_quiz.html", difficulty=difficulty, no_questions=no_questions)



# Page to select settings
# Relevant settings:
## Difficulty
## Number of words
# Page links to quiz, where these settings are read.
@app.route("/settings", methods=["GET"])
def select_settings():
    return render_template("select_quiz_settings.html")


# Standard homepage.
@app.route("/")
def index():
    return render_template("homepage.html")


# Standard about page.
@app.route("/about")
def about():
    return render_template("about_triolingo.html")


if __name__ == '__main__':
    app.run(debug=True)
