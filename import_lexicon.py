import pandas as pd

def import_lexicon():
    # import the vocabulaire
    file = 'Lexicon.csv'
    df = pd.read_csv(file)
    return df
