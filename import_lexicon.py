import pandas as pd

def import_lexicon():
    # import the vocabulaire
#    file = r'C:\Users\Rodger\Documents\Data Science\[Online courses]\Flask learnings\Julian Nash\app\Lexicon.csv'
    file = "./Lexicon.csv"
    df = pd.read_csv(file)
    return df
