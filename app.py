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
    if request.method == "POST":
        print(request.form)
        print(request.form.get("mode"))

        if request.form.get("mode") == "Mastering words":
            print("you have selected mastering words")
        elif request.form.get("mode") == "Mixture":
            print("you have selected a mixture")
        elif request.form.get("mode") == "Learning new words":
            print("you have selected learning new words")

    df = import_lexicon()
    quizzed_dataframe = df.iloc[list_of_numbers]

    i = 0
    text = request.form.get('text')
    print(i)
    print(quizzed_dataframe.iloc[[i]])
    try:
        print(i)
        if text == "Goed antwoord":
            processed_text = text.upper()
            quizzed_data = quizzed_dataframe.iloc[[list_of_numbers[i+1]]]
            return render_template("do_quiz.html", entries=settings,
                               tables=[quizzed_data.to_html(classes="data", header="true")],
                               random_numbers=list_of_numbers, processed_text=processed_text,
                                   formulier=request)
        else:
            processed_text = text
            quizzed_data = quizzed_dataframe.iloc[[list_of_numbers[i]]]
            return render_template("do_quiz.html", entries=settings,
                               tables=[quizzed_data.to_html(classes="data", header="true")],
                               random_numbers=list_of_numbers, processed_text=processed_text,
                                   formulier=request)
    except AttributeError:
        quizzed_data = quizzed_dataframe.iloc[[list_of_numbers[i]]]
        return render_template("do_quiz.html", entries=settings,
                           tables=[quizzed_data.to_html(classes="data", header="true")],
                           random_numbers=list_of_numbers, formulier=request)


@app.route("/json", methods=['POST', 'GET'])
def json():
    if request.is_json:
        req = request.get_json()
        return "JSON received!", 200

    else:
        return "No JSON received!", 400

if __name__ == '__main__':
    app.run(debug=True)