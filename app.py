from flask import Flask, render_template, request
import pandas as pd
from import_lexicon import import_lexicon

app = Flask(__name__)
transactions = []
list_of_numbers = [1, 2, 4]

woordjes = ["hallo", " wereld"]
settings = []


@app.route("/")
def index():
    return render_template("homepage.html")


@app.route("/about")
def about():
    return render_template("about_triolingo.html")


@app.route("/settings", methods=["GET", "POST"])
def select_settings():
    return render_template("select_quiz_settings.html")


@app.route("/form", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        print(request.form)
        print(request.form.get("account"))
        transactions.append(
            (
                request.form.get("date"),
                float(request.form.get("amount")),
                request.form.get("account"),
            )
        )
    return render_template("outdated - form.html")


@app.route("/quiz", methods=['POST', 'GET'])
def quiz_page():
    #mode = str()
    #number_of_questions = int()
    df = import_lexicon()
    quizzed_dataframe = df.iloc[list_of_numbers]

    i = 0
    text = request.form.get('text')
    print(i)
    print(quizzed_dataframe.iloc[[i]])
    print(quizzed_dataframe['Polish'][1])

    # TODO: check whether necessary
    if (request.method == "GET"):
        return render_template("select_quiz_settings.html")

    # After been referred from settings, so start of the quiz
    # Arguments:
    #   settings (TODO: required? miss class maken, self enzo)
    # Arguments passed on:
    #   settings (TODO: required?)
    #   the first word of the quizzes dataframe
    elif (request.method == "POST") & (request.headers.get("Referer")[-9:] == "/settings"):

        mode = request.form.get("mode")
        number_of_questions = request.form.get("amount")

        print(mode, number_of_questions)

        if request.form.get("mode") == "Mastering words":
            difficulty = "mastery"
        elif request.form.get("mode") == "Mixture":
            difficulty = "mixed"
        elif request.form.get("mode") == "Learning new words":
            difficulty = "new"


        quizzed_data = quizzed_dataframe.iloc[[list_of_numbers[i]]]
        if difficulty == "mastery":
            return render_template("do_quiz.html", settings=request,
                                   tables=[quizzed_data.to_html(classes="data", header="true")],
                                   random_numbers=list_of_numbers,
                                   woordje=df['Polish'][1])

        elif difficulty == "mixed":
            return render_template("do_quiz.html", settings=request,
                                   tables=[quizzed_data.to_html(classes="data", header="true")],
                                   random_numbers=list_of_numbers,
                                   woordje=df['Polish'][2])

        elif difficulty == "new":
            return render_template("do_quiz.html", settings=request,
                                   tables=[quizzed_data.to_html(classes="data", header="true")],
                                   random_numbers=list_of_numbers,
                                   woordje=df['Polish'][3])

    elif (request.method == "POST") & (request.headers.get('Referer')[-5:] == "/quiz"):
        #print(mode, number_of_questions)
        try:
            print(i)
            if text == "Goed antwoord":
                processed_text = text.upper()
                quizzed_data = df.iloc[[list_of_numbers[i + 1]]]
                return render_template("do_quiz.html", entries=settings,
                                       tables=[quizzed_data.to_html(classes="data", header="true")],
                                       random_numbers=list_of_numbers, processed_text=processed_text,
                                       formulier=request, woordje=df['Polish'][2])
            else:
                processed_text = text
                quizzed_data = quizzed_dataframe.iloc[[list_of_numbers[i]]]
                return render_template("do_quiz.html", entries=settings,
                                       tables=[quizzed_data.to_html(classes="data", header="true")],
                                       random_numbers=list_of_numbers, processed_text=processed_text,
                                       formulier=request, woordje=df['Polish'][2])
        except AttributeError:
            quizzed_data = quizzed_dataframe.iloc[[list_of_numbers[i]]]
            return render_template("do_quiz.html", entries=settings,
                                   tables=[quizzed_data.to_html(classes="data", header="true")],
                                   random_numbers=list_of_numbers, formulier=request,
                                   woordje=df['Polish'][2])






@app.route("/json", methods=['POST', 'GET'])
def json():
    if request.is_json:
        req = request.get_json()
        return "JSON received!", 200

    else:
        return "No JSON received!", 400


if __name__ == '__main__':
    app.run(debug=True)
