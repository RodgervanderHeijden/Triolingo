## Triolingo (for now)

Welcome to the codebase of Triolingo. Triolingo is a language learning app akin to Duolingo, created solely for the
personal use of Rodger van der Heijden. It is not aimed at serving many needs, yet anyone that does see its benefits is
free to use this project.

## Language learning

Triolingo is a Flask app that allows language users more control over the process of learning another language (in this
case Polish specifically, though other backends should theoretically be easy to slot in). It adds voice commands, has
an option to select the difficulty setting and number of questions and most importantly it provides the sentences in
order of personal (predicted) difficulty. The algorithm is adaptive; as your command of your target language grows,
easy quizzes will remain relatively just as easy as before - the average difficulty of the sentences increases along
your understanding.

## Several learning modes

Though still limited on options - after all it's a WIP - several quizzing options exist. Three possible methods of
providing an answer (will) exist: using open text boxes, selecting an answer in multiple choice or using your voice to
say the answer. Users will soon (at least, hopefully) be able to answer missing words in a sentence, provide
translations of entire sentences, select the correct declensions and conjugations or pick the word order to create the
sentence question.

## Progressing

Triolingo makes use of four 'progress meters': one overall language proficiency meter, and one learning rate parameter
for each difficulty setting (easy, moderate, difficult). The expectation for easy quizzes is 80% correct, for moderate
60% and for difficult ones 30%. Your actual quiz results determine how much the respective learning rate changes. With
repeated scores of 100% your language proficiency value will increase rapidly, sampling ever increasingly difficult
questions.

## Test it out

Try Triolingo out for yourself [here](www.vanderheijden.pythonanywhere.com) (though without any progression or storage
of results; the web demo merely exists to provide an insight to the web app. In case you are a programmer, the code on
this repo requires some additional files, which I'll be happy to provide if you contact me.
