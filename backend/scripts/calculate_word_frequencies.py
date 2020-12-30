from helper_functions import import_tatoeba
import pandas as pd
from collections import Counter
import codecs
import csv
import string

def import_tatoeba():
    """Imports and returns the tatoeba data"""
    with codecs.open("../data/tatoeba/tatoeba_sentences.csv", 'r', encoding="utf-8") as f:
        df_pol_reader = csv.DictReader(f, delimiter=",")
        df_all_sentences = pd.DataFrame(df_pol_reader)[['sentenceID', 'sentence_pl']]
    return df_all_sentences


def import_word_counts():
    """Imports and returns the word counts"""
    with codecs.open("../data/tatoeba/word_counts.csv", 'r', encoding="utf-8") as f:
        df_reader = csv.DictReader(f, delimiter=",")
        df_word_counts = pd.DataFrame(df_reader)
    return df_word_counts


def store_word_counts(df):
    """Takes in a dataframe of format:
    ________________
    | word | count |
    |______|_______|
    and writes to word_counts.csv in format:
    _________________________
    | wordID | word | count |
    |________|______|_______|
    where wordID is assigned here (= index).
    """
    df.reset_index(inplace=True)
    df.columns = ['wordID', 'word', 'count']
    df.to_csv('../data/tatoeba/word_counts.csv', index=False)


def calculate_and_store_sentence_ease(df):
    """
    Takes in a dataframe of format:
    ________________________________________________
    | sentenceID | sentence_pl | words_in_sentence |
    |____________|_____________|___________________|
    and writes to sentence_ease.csv in format:
    ________________________________________________________________
    | sentenceID | sentence_pl | words_in_sentence | sentence_ease |
    |____________|_____________|___________________|_______________|
    where words_in_sentence is defined as the set of cleaned words,
    and sentence_ease is calculated based on the sum of counts of the words, divided by sentence length.
    """
    df_word_counts = import_word_counts()
    df['sentence_ease'] = pd.Series(dtype=float)

    for index, row in df.iterrows():
        if (index % 500 == 0):
            print(index)
        # replace word by df_word_counts.loc[word] om te kijken of dat miss beter is
        sentence_summed_count = sum([int(df_word_counts.loc[df_word_counts['word']==word, 'count']) for word in row['words_in_sentence']])
        sentence_length = len(row['words_in_sentence'])
        sentence_ease = sentence_summed_count/sentence_length

        df.at[index, 'sentence_ease'] = sentence_ease
    df.to_csv('../data/tatoeba/sentence_ease_pl.csv', index=False)


def loop_over_tatoeba():
    word_list = []
    df_polish_sentences = import_tatoeba()
    df_polish_sentences['words_in_sentence'] = pd.Series(dtype=object)
    # No clue why, but the inclusion of index is required for proper functioning
    for index, row in df_polish_sentences.iterrows():
        # Take the sentence, convert it to lowercase,
        # take out any punctuation,
        # split on spaces and convert to a set.
        remove_punctuation = str.maketrans("", "", string.punctuation)
        stripped_sentence = [word for word in row['sentence_pl'].lower().translate(remove_punctuation).split(" ")]
        stripped_sentence_set = set(stripped_sentence)
        # Store the set of words in df_polish_sentences
        df_polish_sentences.at[index, 'words_in_sentence'] = stripped_sentence_set
        # and add the cleaned sentence to the overall word list (used for counts later)
        # I purposely did not append the set but rather the list, as I feel it results in a better count
        [word_list.append(word) for word in stripped_sentence]

    #df_word_counts = pd.DataFrame.from_records(Counter(word_list).most_common(), columns=['word_pl', 'word_pl_count'])
    #store_word_counts(df_word_counts)

    # TODO
    calculate_and_store_sentence_ease(df_polish_sentences)


loop_over_tatoeba()