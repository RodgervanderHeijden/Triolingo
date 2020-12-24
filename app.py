from flask import Flask, render_template, request, url_for, redirect
import pandas as pd
from import_lexicon import import_lexicon

app = Flask(__name__)

list_of_numbers = [1, 2, 4]
global settings
i = [0]
current_question = [0]


@app.route('/quiz_confirmation', methods=["POST"])
def confirm_quiz_settings():
    # De request hier komt van settings af
    # en bestaat dus uit mode en questions
    questions = request.form.get("amount")

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

    difficulty=difficulty
    no_questions=no_questions

    print(difficulty, no_questions)
    df = import_lexicon()
    quizzed_dataframe = df.iloc[list_of_numbers]
    # Tot hier dus
    current_question = 1
    difficulty=difficulty

    # After been referred from settings, so start of the quiz
    # Arguments:
    #   settings (TODO: required? miss class maken, self enzo)
    # Arguments passed on:
    #   settings (TODO: required?)
    #   the first word of the quizzes dataframe
    if (request.method == "POST") & (request.headers.get("Referer")[-9:] == "/settings"):
        # Probably outdated
        settings = request

        quizzed_data = quizzed_dataframe.iloc[[list_of_numbers[i[0]]]]
        if difficulty == "mastery":
            return render_template("do_quiz.html", settings=settings,
                                   tables=[quizzed_data.to_html(classes="data", header="true")],
                                   random_numbers=list_of_numbers,
                                   woordje=df['Polish'][1], current_question=current_question,
                                   )

        elif difficulty == "mixed":
            return render_template("do_quiz.html", settings=settings,
                                   tables=[quizzed_data.to_html(classes="data", header="true")],
                                   random_numbers=list_of_numbers,
                                   woordje=df['Polish'][2], current_question=current_question,
                                   )

        elif difficulty == "new":
            return render_template("do_quiz.html", settings=settings,
                                   tables=[quizzed_data.to_html(classes="data", header="true")],
                                   random_numbers=list_of_numbers,
                                   woordje=df['Polish'][3], current_question=current_question,
                                   )


    #print(number_of_questions)
    #print(current_question, number_of_questions)
    if (request.method == "POST") & (request.headers.get('Referer')[-5:] == "/quiz"):
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
                                       current_question=current_question)
            else:
                processed_text = text
                return render_template("do_quiz.html",
                                       tables=[quizzed_data.to_html(classes="data", header="true")],
                                       random_numbers=list_of_numbers, processed_text=processed_text,
                                       formulier=request, woordje=df['Polish'][2], mode=difficulty,
                                       current_question=current_question)
        except AttributeError:
            return render_template("do_quiz.html",
                                   tables=[quizzed_data.to_html(classes="data", header="true")],
                                   random_numbers=list_of_numbers, formulier=request,
                                   woordje=df['Polish'][2], mode=difficulty,
                                   current_question=current_question)

    #
    # # pseudo
    # if aantal_vragen < no_questions:
    #     do_vraag
    #
    #
    # else:
    #     return redirect("after_quiz.html", difficulty=difficulty, no_questions=no_questions)
    # TODO: send quiz data as argument
    #return redirect("after_quiz.html")
    # TODO: hierin mist de zin/het woord ic en hoeveel van de quiz gedaan is.
    return render_template("do_quiz.html", difficulty=difficulty, no_questions=no_questions)



# TODO: receive quiz data as argument
@app.route("/after_quiz", methods=["GET"])
def show_quiz_data():

    # TODO
    def update_lexicon():
        pass

    return render_template("after_quiz.html")



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
