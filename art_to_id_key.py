import pandas as pd

def make_key(tua):
    '''

    :param tua: dataframe of all the tuas
    :return: nothing; outputs a new csv relating all data of an article
    '''


    singles = tua.drop_duplicates(subset = 'article_sha256')
    singles = singles[['article_sha256', 'article_filename','article_number']]
    singles.to_csv('filename_to_sha256_key', encoding='utf-8')