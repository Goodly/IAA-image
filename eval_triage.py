import pandas as pd


def eval_triage_scoring(tua, pointsdf, directory):
    '''
    Calculates point additions/deductions based off of the TUAs used to generate tasks
    In the future I'll set up a csv to tune this.  For now I can't think of a good way to do that so I'll try to make
    the code super clear
    :param tua: dataframe of both tuas
    :param pointsdf: dataframe of sortedpts
    :return:
    '''
    overallChange = pd.DataFrame(
        columns=("Schema", 'agreement_adjusted_points', 'Label', 'article_num', 'article_sha256'))
    for art_sha256 in tua['article_sha256'].unique():
        art_tua = tua[tua['article_sha256'] == art_sha256]
        art_num = art_tua['article_number'].iloc[0]
        art_length = art_tua['article_text_length'].iloc[0]
        if art_length < 800:
            continue
        # This is a constant, relatively arbitrary, try different values
        base_article_len = 2800
        article_size_index = art_length / base_article_len
        num_assertions = count_cases(art_tua, 'Assertions')
        num_args = count_cases(art_tua, 'Arguments')
        num_sources = count_cases(art_tua, 'Quoted Sources')
        num_evidence = count_cases(art_tua, 'Evidence')

        # check if low information
        information_count = num_args + num_sources + num_evidence
        information_index = information_count / article_size_index
        # Guidance from spreadsheet has these values at -15 for <3 and -5 for <4; I'm hesitant to make it -15 until we
        # make sure that case rarely occurs
        if information_index < 3 and information_count < 5:
            overallChange = addPoints(overallChange, -10, 'Very Low Information', art_num, art_sha256)
        elif information_index < 4 and information_count < 8:
            points = -5*(4-information_index)
            overallChange = addPoints(overallChange, points, 'Low Information', art_num, art_sha256)

        # check if article is assertion-happy--triager instruction is that it's only an assertion if it's a rogue claim
        # not backed by anything in the article so these are bad
        assertion_index = num_assertions / article_size_index


        if assertion_index >= 5 and information_count < 5:
            assertion_indices = getIndices(art_tua, 'Assertions')
            overallChange = addPoints(overallChange, -12, 'Unsupported Assertions', art_num, art_sha256,
                                      indices=str(assertion_indices))
        elif assertion_index >= 2 and information_count < 8:
            assertion_indices = getIndices(art_tua, 'Assertions')
            points = -4*(assertion_index-2)
            overallChange = addPoints(overallChange, points, 'Unsupported Assertions', art_num, art_sha256,
                                      indices=str(assertion_indices))


    # Code below from previous version where triage tasks were used to holisticall evaluate article
    # workflow is to do one thing at a time
    # cb_tua = tua[tua['topic_name'] == 'Clickbait Title']
    # for i in range(len(cb_tua)):
    #     art_num = cb_tua['article_number'].iloc[i]
    #     art_id = cb_tua['article_sha256'].iloc[i]
    #     overallChange = addPoints(overallChange, -10, 'Clickbait Title', art_num, art_id)
    #
    # bias_tua = tua[tua['topic_name'] == 'Bias']
    # for i in range(len(bias_tua)):
    #     targ = bias_tua['target_text'].iloc[i].strip()
    #     art_num = bias_tua['article_number'].iloc[i]
    #     art_id  = bias_tua['article_sha256'].iloc[i]
    #     if targ.lower() == 'a':
    #         overallChange = addPoints(overallChange, 5, 'Circumspect', art_num, art_id)
    #     elif targ.lower() == 'b':
    #         overallChange = addPoints(overallChange, 0, 'Balanced', art_num, art_id)
    #     elif targ.lower() == 'c':
    #         overallChange = addPoints(overallChange, -5, 'Biased', art_num, art_id)
    #     elif targ.lower() == 'd':
    #         overallChange = addPoints(overallChange, -10, 'Very Biased', art_num, art_id)
    #
    # genre_tua = tua[tua['topic_name'] == 'Genre']
    # for i in range(len(genre_tua)):
    #     targ = genre_tua['target_text'].iloc[i].strip()
    #     art_num = genre_tua['article_number'].iloc[i]
    #     art_id  = genre_tua['article_sha256'].iloc[i]
    #     if targ.lower() == 'n':
    #         overallChange = addPoints(overallChange, 0, 'Genre -- News', art_num, art_id)
    #     elif targ.lower() == 'o':
    #         overallChange = addPoints(overallChange, 0, 'Genre -- Opinion', art_num, art_id)
    #     elif targ.lower() == 'p':
    #         overallChange = addPoints(overallChange, -10, 'Genre -- Hyper-Partisan', art_num, art_id)
    #     elif targ.lower() == 'g':
    #         overallChange = addPoints(overallChange, -10, 'Genre -- Celebrity Gossip', art_num, art_id)
    #     elif targ.lower() == 'h':
    #         overallChange = addPoints(overallChange, 0, 'Genre -- Health News', art_num, art_id)
    #     elif targ.lower() == 's':
    #         overallChange = addPoints(overallChange, 0, 'Genre -- Science', art_num, art_id)

    pointsdf = pd.concat([pointsdf, overallChange], axis=0, ignore_index=True)
    pointsdf.to_csv(directory + '/AssessedPoints.csv')

def points_by_distance(value, target, scale,min = 0, max = 20):
    """
    finds points based on distance from target value.  Assumes value is in the wrong direction; ie if we want target of
    at least 4, value is 3.5; or if we want target of at most 5, value is 4.2
    can't go higher than the max
    Commonly, scale gets steeper for more extreme infractions
    """
    points = abs(target-value)*scale
    if points>max:
        return max
    return max(points, min)*-1
def getIndices(tua, topic):
    topic_tua = tua[tua['topic_name'] == topic]
    indices = []
    for i in range(len(topic_tua)):
        start = topic_tua['start_pos'].iloc[i]
        end = topic_tua['end_pos'].iloc[i]
        for n in range(start, end):
            indices.append(n)
    return indices


def count_cases(tua, topic):
    topical_tua = tua[tua['topic_name'] == topic]
    if len(topical_tua)<1:
        return 0
    # in current implementation highest case number is the # of cases; always starts at 1 counts up
    case_nums = topical_tua['case_number']
    return len(case_nums.unique())


def addPoints(df, points, label, art_num, art_id, indices='[]'):
    df = df.append({'Schema': 'Overall', 'agreement_adjusted_points': points, 'Label': label, 'article_num': art_num,
                    'article_sha256': art_id, 'highlighted_indices': indices}, ignore_index=True)
    return df
