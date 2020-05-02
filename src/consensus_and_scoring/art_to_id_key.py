import pandas as pd
from pointAssignment import pointSort
def make_key(tua, directory, prefix = ''):
    '''

    :param tua: dataframe of all the tuas
    :return: nothing; outputs a new csv relating all data of an article
    '''


    singles = tua.drop_duplicates(subset = 'article_sha256')
    singles = singles[['article_sha256', 'article_filename','article_number']]
    singles['article_url'] = 'publiceditor.io/Articles/Visualization'+prefix+ singles['article_sha256'] + '.html'
    singles.to_csv(directory+'/filename_to_sha256_key.csv', encoding='utf-8')
    print('keymade')

#tuas, weights = pointSort('scoring_nyu_6_raw_60', 'nyu_6_raw_60')
#make_key(tuas, 'scoring_nyu_6_raw_60', prefix = 'raw_60')