from flask import Flask, render_template, request, url_for, redirect
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
                           questions=questions, current_question=1)


@app.route("/quiz/<difficulty>/<no_questions>/", methods=["POST"])
def quiz_page(difficulty="mastery", no_questions=10):

    print(request)
    print(request.form)

    # Get from URL
    difficulty=difficulty
    no_questions=int(no_questions)
    print(difficulty, no_questions)

    # TODO: call python script (via import) that returns a df with to be quizzed vocab
    df = import_lexicon()
    quizzed_dataframe = df.iloc[list_of_numbers]

    answer_bool = request.form.get('text', None)
    print(i)
    previous_q = i[0]
    next_q = previous_q+1
    i.append(next_q)
    i.pop(0)
    print(i)
    print(i)
    print(i)
    print(i)
    while i[0] < no_questions:

        if (request.method == "POST") & (answer_bool is None):
            i[0] = int(0)
            return render_template("do_quiz.html", difficulty=difficulty, no_questions=no_questions)

        elif (request.method == "POST") & (answer_bool is not None):
            # TODO
            # check whether answer is correct
            return render_template("do_quiz.html", difficulty=difficulty, no_questions=no_questions,
                                   answer=answer_bool)

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
