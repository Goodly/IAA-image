
import pandas as pd


def eval_triage_scoring(tua, pointsdf, directory):
    '''

    :param tua: dataframe of both tuas
    :param pointsdf: dataframe of both tuas
    :return:
    '''
    overallChange = pd.DataFrame(columns = ("Schema", 'agreement_adjusted_points', 'Label', 'article_num', 'article_sha256'))
    #workflow is to do one thing at a time
    cb_tua = tua[tua['topic_name'] == 'Clickbait Title']
    for i in range(len(cb_tua)):
        art_num = cb_tua['article_number'].iloc[i]
        art_id = cb_tua['article_sha256'].iloc[i]
        overallChange = addPoints(overallChange, -10, 'Clickbait Title', art_num, art_id)

    bias_tua = tua[tua['topic_name'] == 'Bias']
    for i in range(len(bias_tua)):
        targ = bias_tua['target_text'].iloc[i].strip()
        art_num = bias_tua['article_number'].iloc[i]
        art_id  = bias_tua['article_sha256'].iloc[i]
        if targ.lower() == 'a':
            overallChange = addPoints(overallChange, 5, 'Circumspect', art_num, art_id)
        elif targ.lower() == 'b':
            overallChange = addPoints(overallChange, 0, 'Balanced', art_num, art_id)
        elif targ.lower() == 'c':
            overallChange = addPoints(overallChange, -5, 'Biased', art_num, art_id)
        elif targ.lower() == 'd':
            overallChange = addPoints(overallChange, -10, 'Very Biased', art_num, art_id)

    genre_tua = tua[tua['topic_name'] == 'Genre']
    for i in range(len(genre_tua)):
        targ = genre_tua['target_text'].iloc[i].strip()
        art_num = genre_tua['article_number'].iloc[i]
        art_id  = genre_tua['article_sha256'].iloc[i]
        if targ.lower() == 'n':
            overallChange = addPoints(overallChange, 0, 'Genre -- News', art_num, art_id)
        elif targ.lower() == 'o':
            overallChange = addPoints(overallChange, 0, 'Genre -- Opinion', art_num, art_id)
        elif targ.lower() == 'p':
            overallChange = addPoints(overallChange, -10, 'Genre -- Hyper-Partisan', art_num, art_id)
        elif targ.lower() == 'g':
            overallChange = addPoints(overallChange, -10, 'Genre -- Celebrity Gossip', art_num, art_id)
        elif targ.lower() == 'h':
            overallChange = addPoints(overallChange, 0, 'Genre -- Health News', art_num, art_id)
        elif targ.lower() == 's':
            overallChange = addPoints(overallChange, 0, 'Genre -- Science', art_num, art_id)



    pointsdf = pd.concat([pointsdf, overallChange], axis = 0, ignore_index=True)
    pointsdf.to_csv(directory+'/AssessedPoints.csv')



def addPoints(df, points, label, art_num, art_id):
    df = df.append({'Schema' : 'Overall', 'agreement_adjusted_points' : points, 'Label':label, 'article_num': art_num,
                    'article_sha256': art_id, 'highlighted_indices': '[]'}, ignore_index=True)
    return df



