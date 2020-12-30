import pandas as pd
import csv
import codecs
import numpy as np

df_sentences = pd.DataFrame()


def import_and_write_polish():
    with codecs.open(r"../data/tatoeba/pol_sentences.tsv", 'r', 'utf-8') as f:
        df_pol_reader = csv.reader(f, delimiter="\t", )
        df_pol_return = pd.DataFrame(df_pol_reader)[[0, 2]]
    df_pol_return.columns = ['sentenceID', 'sentence_pl']
    return df_pol_return


def match_links(df):
    with open(r"../data/tatoeba/links.csv",
              newline='') as f:
        df_links_reader = csv.reader(f, delimiter="\t", )
        df_links = pd.DataFrame(df_links_reader, columns=['sentenceID', 'matched_sentenceID'])
    df_return = df.merge(df_links, how='left', left_on=['sentenceID'], right_on=['sentenceID'])
    return df_return


def import_and_write_english(df):
    with codecs.open(r"../data/tatoeba/eng_sentences.tsv", 'r', 'utf-8') as f:
        df_eng_reader = csv.reader(f, delimiter="\t", )
        df_eng_data = pd.DataFrame(df_eng_reader)[[0, 1, 2]]
    df_eng_data.columns = ['sentenceID_en', 'lang', 'sentence_en']
    df_return = df.merge(df_eng_data, how='left', left_on=['matched_sentenceID'], right_on=['sentenceID_en'])
    return df_return


def import_and_write_dutch(df):
    with codecs.open(r"../data/tatoeba/nld_sentences.tsv", 'r', 'utf-8') as f:
        df_nl_reader = csv.reader(f, delimiter="\t", )
        df_nl_data = pd.DataFrame(df_nl_reader)[[0, 1, 2]]
    df_nl_data.columns = ['sentenceID_nl', 'lang', 'sentence_nl']
    df_return = df.merge(df_nl_data, how='left', left_on=['matched_sentenceID'], right_on=['sentenceID_nl'],
                         suffixes=('_left', '_right'))
    return df_return


def clean_and_store_results(df):
    # drop polish sentences with neither an English nor Dutch translation
    df.dropna(subset=['sentenceID_nl', 'sentenceID_en'], how='all',
              axis=0, inplace=True)
    df['lang'] = np.where(df['lang_left'].notna(), 'en', 'nl')
    df.drop(labels=['lang_left', 'lang_right',
                    'sentenceID_nl', 'sentenceID_en',
                    'matched_sentenceID'], axis=1, inplace=True)
    print(df.columns)
    df.reset_index(drop=True, inplace=True, )
    df.to_csv('../data/tatoeba/tatoeba_sentences.csv', index=False)


def create_tatoeba_lexicon():
    df_pl = import_and_write_polish()
    df_pl_match = match_links(df_pl)
    df_pl_en = import_and_write_english(df_pl_match)
    df_pl_en_nl = import_and_write_dutch(df_pl_en)
    clean_and_store_results(df_pl_en_nl)


create_tatoeba_lexicon()
