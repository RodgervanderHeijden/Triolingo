import pandas as pd
import numpy as np

from scipy.stats import linregress
import matplotlib.pyplot as plt

import datetime

from colorama import Fore
from IPython.display import clear_output, display
from ipywidgets import IntSlider, Output
import ast


# %%

def do_quiz1(no_of_q=3):
    correct = 0
    false = 0
    previous_n = -1
    out = Output()
    words = Output()
    inp = Output()

    clear = Output()

    with words:
        print(df_lexicon['Polish'][correct])

    with clear:
        clear_output()

    while no_of_q > correct:
        print(no_of_q, correct)
        display(words)
        correct += 1
        display(clear)

        # user_input = input()
        # with out:
        #   user_input = input()
        # display(out)

        # if user_input == df_lexicon['Dutch'][correct]:
        #   correct += 1
        #  with out:
        #     clear_output()
        # display(out)


do_quiz1()

# %%

df_lexicon['Polish'][0]


# %%

# for calculating your knowledge and ordering the words
def update_scores():
    # predict the number of correct answers based on the amount of tries
    # calculate slope and intercept (other vars are required, but not used)
    slope, intercept, r_value, p_value, std_err = linregress((df_lexicon['Correct'] + df_lexicon['False']),
                                                             df_lexicon['Correct'])
    # calculate residuals based on slope and intercept
    df_lexicon['Residuals'] = df_lexicon['Correct'] - (
                slope * (df_lexicon['Correct'] + df_lexicon['False']) + intercept)

    # however, as the residuals of words with just a few tries will be low
    # eg (0correct,0false) has a low resid, (0,1) or (1,3) as well
    # I manually set the residual-value of words <= 8 tries (arbitrary border)
    # to -0.5, which as of now has them starting around position 30 (arbitrary position).
    df_lexicon.loc[((df_lexicon['Correct'] + df_lexicon['False']) <= 5), 'Residuals'] = -1.5

    # similarly, but to a more extreme extend, the words with fewer than
    # 4 tries will get a residual of -1.5, starting them at #20 as of now
    df_lexicon.loc[((df_lexicon['Correct'] + df_lexicon['False']) <= 2), 'Residuals'] = -3

    # sort on residual and reset index
    df_lexicon.sort_values(by='Residuals', inplace=True, ascending=True)
    df_lexicon.reset_index(drop=True, inplace=True)

    # save results as xlsx
    writer = pd.ExcelWriter('Lexicon.xlsx')
    df_lexicon.to_excel(writer, 'Words')
    writer.save()
    # save results as csv
    df_lexicon.to_csv('Lexicon.csv', encoding='utf-8', index=False)


update_scores()


# %% md

## also add: check when adding words whether they're already in the df

# %%

# for adding words
def add_words(polish, dutch, english):
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    pd.to_datetime(date)

    df_lexicon.loc[len(df_lexicon)] = [polish, [dutch], [english], 0, 0, str(date), 0]
    print('Jeszcze raz?')
    answer = input()
    if answer == "n":
        writer = pd.ExcelWriter('Lexicon.xlsx')
        df_lexicon.to_excel(writer, 'Words')
        writer.save()
    else:
        a = answer
        b = input()
        c = input()
        add_words(a, b, c)
    clear_output()
    update_scores()


# %%

# "legacy" code
# works(-ish)

# MAAR
# je kunt niet extra opties toevoegen!!

def clear():
    clear_output(wait=True)


def do_quiz(no_of_q=20):
    correct = 0
    false = 0
    false_queue = []
    previous_n = -1

    # quiz
    while no_of_q > correct:
        r = np.random.randint(1, 100)
        if r <= 50:  # 60% chance to have one of the first 10% of words
            n = np.random.randint(0, (len(df_lexicon) * .15))
        elif r <= 95:  # 35% chance for one of the words percentage 10 to 40
            n = np.random.randint(len(df_lexicon) * .15, len(df_lexicon) * .50)
        else:  # remaining 5% chance of the last 60% of words
            n = np.random.randint(20, len(df_lexicon))

        # clear_output()
        print(Fore.BLACK + df_lexicon['Polish'][n])
        # print(n, df_lexicon['Residuals'][n])
        # print(correct, false, no_of_q)

        # HERE:
        # print word color based on category it's from/residuals

        user_answer = input()
        # print(user_answer)

        if user_answer == 'n':
            break

        elif user_answer == "lul nie":
            if previous_n != -1:
                df_lexicon.loc[previous_n, 'False'] -= 1
                df_lexicon.loc[previous_n, 'Correct'] += 1
                false_queue.remove(previous_n)
                # clear_output() clearing output removes the input()-prompt,
                # even when specifically called again
                # maybe research why at a later moment

                print("Vooruit dan makker")
                user_answer = input("In what language?")

                if user_answer == "nl":
                    print("Toegevoegd aan antwoorden")
                    df_lexicon.loc[previous_n, 'Dutch'] = ast.literal_eval(df_lexicon.loc[previous_n, 'Dutch']).append(
                        previous_answer)
                elif user_answer == "en":
                    print("Added to answers")
                    df_lexicon.loc[previous_n, 'English'] = ast.literal_eval(
                        df_lexicon.loc[previous_n, 'English']).append(previous_answer)

                print(df_lexicon['Polish'][n])
                previous_n = -1
                correct += 1
                false -= 1
                user_answer = input()

        try:
            assert user_answer in ast.literal_eval(df_lexicon['Dutch'][n]) or user_answer in ast.literal_eval(
                df_lexicon['English'][n])
            correct += 1
            # clear_output()
            print(Fore.GREEN + "Correct!")
            df_lexicon.loc[n, 'Correct'] += 1
            # clear()
            # print(no_of_q, correct)

        except AssertionError:
            previous_n = n
            false += 1
            # clear_output()
            print(Fore.RED + "Your translation of '{0:5s}' for '{1:5s}' is not correct.".format(user_answer,
                                                                                                df_lexicon['Polish'][
                                                                                                    n]))
            print(Fore.RED + "Try '{0:5s}' or '{1:5s}' next time!".format(ast.literal_eval(df_lexicon['English'][n])[0],
                                                                          ast.literal_eval(df_lexicon['Dutch'][n])[0]))
            df_lexicon.loc[n, 'False'] += 1
            false_queue.append(n)

        # progress
        if correct == (np.floor(no_of_q / 2)):
            print(Fore.GREEN + "Halfway there!")
        if correct == (np.floor(no_of_q * .75)):
            print(Fore.GREEN + "Almost there! Keep going!")
        if correct == no_of_q:
            print(Fore.GREEN + "Finished with your original questions!")
            for n in false_queue:
                print(Fore.BLUE + df_lexicon['Polish'][n])

        previous_n = n
        previous_answer = user_answer

    # repetition of incorrect words
    while false_queue != []:
        for mistake in false_queue:
            print(false_queue)
            print(Fore.BLACK + "Only {0:3.0F} left to do!".format(len(false_queue)))
            print(Fore.BLACK + df_lexicon['Polish'][mistake])
            user_answer = input("Translation: ")

            if user_answer == "lul nie":
                if previous_n != -1:
                    df_lexicon.loc[previous_mistake, 'False'] -= 1
                    false_queue.remove(previous_mistake)
                    # clear_output()
                    print("Vooruit dan makker")
                    print(df_lexicon['Polish'][mistake])
                    previous_mistake = -1
                user_answer = input()

            try:
                assert user_answer in ast.literal_eval(df_lexicon['Dutch'][mistake]) or user_answer in ast.literal_eval(
                    df_lexicon['English'][mistake])
                # clear_output()
                print(Fore.GREEN + "Correct!")
                false_queue.remove(mistake)

            except AssertionError:
                # clear_output()
                print(Fore.RED + "Your translation of '{0:5s}' for '{1:5s}' is not correct.".format(user_answer,
                                                                                                    df_lexicon[
                                                                                                        'Polish'][
                                                                                                        mistake]))
                print(Fore.RED + "Try '{0:5s}' or '{1:5s}' next time!".format(
                    ast.literal_eval(df_lexicon['English'][mistake])[0],
                    ast.literal_eval(df_lexicon['Dutch'][mistake])[0]))
                false_queue.append(mistake)
                df_lexicon.loc[mistake, 'False'] += 1

            previous_mistake = mistake

    print(Fore.BLACK + "Finished, great job!")
    print(Fore.BLACK + "Your final score is {0:3.1F}".format(float(10 * correct / (correct + false))))

    update_scores()
    print(sum(df_lexicon['Residuals']))


# %%

do_quiz(15)

# %% raw

# %%


# %%

df_copy = df_lexicon.copy()
print("Toegevoegd aan antwoorden")
temp = df_copy.loc[1, 'Dutch']
temp
# = temp.append('ook al')

# df_copy.head(5)

# %%

print([x for x in (df_copy.loc[3, 'Dutch'])])

#      , 'ook goed'])
temp = df_copy.loc[2, 'Dutch']
temp.append('ok')

df_copy.at[3, 'Dutch'] = [df_copy.loc[3, 'Dutch'], 'ook goed']

# %%

temp.append("oa")
temp

# %%

df_copy.head(5)

# %%

pools_t = [['[a]'], ['[b]'], ['[c]']]
nl_t = ['1', '2', '3']
df_temp = pd.DataFrame({'pools_t': pools_t, 'nl_t': nl_t})
df_temp

# %%

b = df_temp.loc[0, 'pools_t']
b.append('ok')
b


# %%

def clear():
    clear_output(wait=True)


def do_quiz1(no_of_q=20):
    correct = 0
    false = 0
    previous_n = -1

    while no_of_q > correct:
        n = np.random.randint(0, 10)
        print(df_lexicon['Polish'][n])
        print(no_of_q, correct, false)
        user_answer = input()

        try:
            assert user_answer in ast.literal_eval(df_lexicon['Dutch'][n]) or user_answer in ast.literal_eval(
                df_lexicon['English'][n])
            correct += 1
            print(Fore.GREEN + "Correct!")
            clear()
            print(no_of_q, correct)

        except AssertionError:
            previous_n = n
            false += 1
            print(Fore.RED + "Your translation of '{0:5s}' for '{1:5s}' is not correct.".format(user_answer,
                                                                                                df_lexicon['Polish'][
                                                                                                    n]))
            print(Fore.RED + "Try '{0:5s}' or '{1:5s}' next time!".format(ast.literal_eval(df_lexicon['English'][n])[0],
                                                                          ast.literal_eval(df_lexicon['Dutch'][n])[0]))

        previous_n = n
        previous_answer = user_answer


# %%

do_quiz1()

# %%

a = 2

# %%


# %%


# %%

df_lexicon.loc[520:, 'Dutch']

# %%

df_lexicon.loc[521]

# %%

antwoord = 'dat'
assert antwoord in df_lexicon['Dutch'][521] or antwoord in df_lexicon['English'][521]
print(Fore.RED + "Try '{0:5s}' or '{1:5s}' next time!".format(df_lexicon['English'][521], df_lexicon['Dutch'][521]))

# %%

assert 't' in ast.literal_eval(df_lexicon['English'][521])

# %%

sum(df_lexicon['Residuals']), 100 * sum(df_lexicon['Correct']) / (
            sum(df_lexicon['Correct']) + sum(df_lexicon['False'])), sum(df_lexicon['Correct']) + sum(
    df_lexicon['False']),

# %%

sum(df_lexicon['Residuals']), 100 * sum(df_lexicon['Correct']) / (
            sum(df_lexicon['Correct']) + sum(df_lexicon['False'])), sum(df_lexicon['Correct']) + sum(
    df_lexicon['False']),

# %%

# To see the words with < 3 tries
df_lexicon[:26]

# %%

# To see the words with < 6 tries
df_lexicon[20:165]

# %%

df_lexicon.Residuals.value_counts()

# %%


# %%

for i in range(len(df_lexicon)):
    f = {df_lexicon.loc[i, 'English']}
    print(f)
    df_lexicon.loc[i, 'English'] = f

    g = {df_lexicon.loc[i, 'Dutch']}
    print(g)
    df_lexicon.loc[i, 'Dutch'] = g
df_lexicon

# %%

for i in range(len(df_lexicon)):
    k = df_lexicon.loc[i, 'Dutch'].pop()
    print(k)
    l = [k]
    df_lexicon.loc[i, 'Dutch'] = l

# %%

df_lexicon

# %%


# %%


# %%


# %%


# %%

add_words(input(), input(), input())

# %%

d = {'col4': [['airconditioning', 'air conditioning'], [2]], 'col2': [3, 4], 'col3': ['janjaap', 'freque']}
df_test = pd.DataFrame(data=d)
df_test

# %%

df_test['col4'][0]

# %%

n = 'airco'

assert n in df_test['col4'][0]

# %%

df_test['col4'][0]

# %%


# %%


# %%


# %%


# %%

file_list = ['C:/Users/Rodger/Documents/Data Science/[Portfolio]/Learning Polish/pl196x/a-publi.xml',
             ]

# %%

# Convert xml to string
# this is required since two tags near the end of the file throw errors
# so they will have to be removed


df_ = pd.DataFrame()

for path in file_list:
    xml_string = ""
    f = open(path, encoding='utf-8')

    for line in f:
        line = line.strip()
        xml_string += line

    xml_string = xml_string[:7755222] + xml_string[7755235:]

    element = ET.fromstring(xml_string)
    tree = ET.ElementTree(element)
    root = tree.getroot()
    print("Just finished: " + path)

    all_text = [(txt.tag) for txt in root.iter('text')]
    # all_words = [(elem.text, elem.get('lemma'), elem.tag) for elem in root.iter()]

    # df_ = df_.append(all_words)

# df_.columns = ['word', 'lemma', 'id']

# %%

all_text

# %%

raw_txt[0:500]

# %%


# %%


# %%

raw_txt_2 = raw_txt[73:148]
element = ET.fromstring(raw_txt_2)
tree = ET.ElementTree(element)
root = tree.getroot()

# %%

all_text = [(txt.attrib) for txt in root.iter('text')]

# %%

all_text

# %%


# %%


# %%


# %%

import nltk
from urllib import request
import requests

# %%

url = "https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/Polish_wordlist"
html = requests.get(url)
page_content = BeautifulSoup(html.content, 'html.parser')

polishWords = []
for i in range(0, 5000):
    words = page_content.find_all("li")[i].text
    polishWords.append(words.split(' ', 1)[0])

polishWords[0:30]
