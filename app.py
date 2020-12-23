from flask import Flask, render_template, request, url_for
import pandas as pd
from import_lexicon import import_lexicon

app = Flask(__name__)
transactions = []
list_of_numbers = [1, 2, 4]
global settings
i = [0]

@app.route("/quiz", methods=['POST'])
def quiz_page():
    df = import_lexicon()
    quizzed_dataframe = df.iloc[list_of_numbers]

    mode = request.form.get("mode")
    questions = request.form.get("amount")
    current_question = 1
    if request.form.get("mode") == "Mastering words":
        difficulty = "mastery"
    elif request.form.get("mode") == "Mixture":
        difficulty = "mixed"
    elif request.form.get("mode") == "Learning new words":
        difficulty = "new"

    # After been referred from settings, so start of the quiz
    # Arguments:
    #   settings (TODO: required? miss class maken, self enzo)
    # Arguments passed on:
    #   settings (TODO: required?)
    #   the first word of the quizzes dataframe
    if (request.method == "POST") & (request.headers.get("Referer")[-9:] == "/settings"):


        # Probably outdated
        number_of_questions = request.form.get("amount")
        settings = request
        print(mode, number_of_questions)


        quizzed_data = quizzed_dataframe.iloc[[list_of_numbers[i[0]]]]
        if difficulty == "mastery":
            return render_template("do_quiz.html", settings=settings,
                                   tables=[quizzed_data.to_html(classes="data", header="true")],
                                   random_numbers=list_of_numbers,
                                   woordje=df['Polish'][1], mode=mode,
                                   questions=questions, current_question=current_question)

        elif difficulty == "mixed":
            return render_template("do_quiz.html", settings=settings,
                                   tables=[quizzed_data.to_html(classes="data", header="true")],
                                   random_numbers=list_of_numbers,
                                   woordje=df['Polish'][2], mode=mode,
                                   questions=questions, current_question=current_question)

        elif difficulty == "new":
            return render_template("do_quiz.html", settings=settings,
                                   tables=[quizzed_data.to_html(classes="data", header="true")],
                                   random_numbers=list_of_numbers,
                                   woordje=df['Polish'][3], mode=mode,
                                   questions=questions, current_question=current_question)

    elif (request.method == "POST") & (request.headers.get('Referer')[-5:] == "/quiz"):
        previous_q = i[0]
        next_q = previous_q+1
        i.append(next_q)
        i.pop(0)
        print(i)
        print(i)
        print(i)
        print(i)
        print(i)
        text = request.form.get('text')
        # i now properly works
        # TODO: make i[0] a subscript to actually present the correct word.
        quizzed_data = quizzed_dataframe.iloc[[0]]
        try:
            #print(i)
            if text == "Goed antwoord":
                processed_text = text.upper()
                return render_template("do_quiz.html",
                                       tables=[quizzed_data.to_html(classes="data", header="true")],
                                       random_numbers=list_of_numbers, processed_text=processed_text,
                                       formulier=request, woordje=df['Polish'][2], mode=difficulty,
                                       questions=questions, current_question=current_question)
            else:
                processed_text = text
                return render_template("do_quiz.html",
                                       tables=[quizzed_data.to_html(classes="data", header="true")],
                                       random_numbers=list_of_numbers, processed_text=processed_text,
                                       formulier=request, woordje=df['Polish'][2], mode=mode,
                                       questions=questions, current_question=current_question)
        except AttributeError:
            return render_template("do_quiz.html",
                                   tables=[quizzed_data.to_html(classes="data", header="true")],
                                   random_numbers=list_of_numbers, formulier=request,
                                   woordje=df['Polish'][2], mode=mode,
                                   questions=questions, current_question=current_question)


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
