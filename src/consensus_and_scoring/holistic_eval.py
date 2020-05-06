import pandas as pd
import os


def eval_triage_scoring(tua, pointsdf, scoring_dir, threshold_func='logis_0', reporting = False):
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
    quoted_sources = get_dep_iaa(scoring_dir, schema="source")
    holistic = get_dep_iaa(scoring_dir, schema="holistic")
    for art_sha256 in tua['article_sha256'].unique():
        if holistic!=None:
            art_holistic = holistic[holistic['article_sha256'] == art_sha256]
        else:
            art_holistic  =None
        art_tua = tua[tua['article_sha256'] == art_sha256]
        art_num = art_tua['article_number'].iloc[0]
        art_id = threshold_func + art_sha256
        art_length = art_tua['article_text_length'].iloc[0]
        if quoted_sources!= None:
            art_sources = quoted_sources[quoted_sources['article_sha256'] == art_sha256]
        else:
            art_sources = None
        if art_length < 800:
            continue
        # This is a constant, relatively arbitrary, try different values
        base_article_len = 2800
        article_size_index = art_length / base_article_len
        num_assertions = count_cases(art_tua, 'Assertions')
        num_args = count_cases(art_tua, 'Arguments')
        num_sources = count_cases(art_tua, 'Quoted Sources')
        num_evidence = count_cases(art_tua, 'Evidence')

        # Handle Quoted Sources Schema here:
        num_vague_quals = 0
        num_vague_sources = 0
        if art_sources !=None:
            for task in art_sources['quiz_task_uuid'].unique():
                task_df = art_sources[art_sources['quiz_task_uuid'] == task]
                task_df['question_Number'] = task_df['question_Number'].apply(int)
                # handle Q2 (koalifications)
                # Can't be done on weightin.py because has to count number of occurrences of the same error.
                q2_df = task_df[task_df['question_Number'] == 2]
                if len(q2_df) > 0:
                    q2scored = False
                    ans = str(q2_df['agreed_Answer'].iloc[0])
                    # q2.a1
                    if ans == '1':
                        points = 2
                        desc = 'Qualified Source'
                        q2scored = True
                    # q2.a2
                    elif ans == '2':
                        points = 1
                        desc = 'Qualified Source'
                        q2scored = True
                    # q2.a3
                    elif ans == '3':
                        points = -1
                        num_vague_quals += 1
                        desc = 'Vaguely Sourced'
                        q2scored = True
                    # q2.a7
                    elif ans == '7':
                        points = -1
                        desc = 'Unqualified Source'
                        q2scored = True
                    # q2.a8
                    elif ans == '8':
                        points = -2
                        desc = 'Unqualified Source'
                        q2scored = True
                    if q2scored:
                        tua_uuid = q2_df['tua_uuid'].iloc[0]
                        indices = get_indices_by_uuid(tua, tua_uuid)
                        overallChange = addPoints(overallChange, points, desc, art_num, art_sha256, art_id,
                                                  indices=str(indices))
            # Handle q5 (identification)

            # >> Scoring note: If ONLY 1.05.07, 1.05.08, or 1.05.09 (i.e not any of the others) then -2 points for each
            # source ... and if there are 2 or more such vague sources in a short article (or 3 in a long article), the
            # article should be dinged -5pts and tagged as 'vague sourcing'
            q5_df = task_df[task_df['question_Number'] == 5]
            q5_df = q5_df.loc[q5_df.agreed_Answer != 'U']
            q5_df = q5_df.loc[q5_df.agreed_Answer != 'M']
            q5_df = q5_df.loc[q5_df.agreed_Answer != 'L']
            if len(q5_df) > 0:
                ans = q5_df['agreed_Answer'].apply(int).tolist()
                if min(ans) > 6:
                    tua_uuid = q5_df['tua_uuid'].iloc[0]
                    indices = get_indices_by_uuid(tua, tua_uuid)
                    num_vague_sources += 1
                    overallChange = addPoints(overallChange, -2, 'Vague Sourcing', art_num, art_sha256, art_id,
                                              indices=str(indices))
        vagueness_index = (num_vague_sources + num_vague_quals) / article_size_index
        if vagueness_index > 4:
            overallChange = addPoints(overallChange, -10, 'Vague Sourcing', art_num, art_sha256, art_id)



        if (num_assertions - num_args - num_sources - num_evidence) > -1:
            # 5aff36a3-f8c5-4e24-b28f-6b1bc7527694 T1.Q1.A1 News report
            if checkArtType(1,1, art_holistic):
                overallChange = addPoints(overallChange, -5, 'Low Information', art_num, art_sha256, art_id)
            else:
                overallChange = addPoints(overallChange, -2, 'Low Information', art_num, art_sha256, art_id)
        # a2f97bce-2512-43e0-9605-0d137d30d8e6 T1.Q1.A3 Op-Ed
        if not checkArtType(1,3, art_holistic):
            indexVal = (1 + num_assertions) / (1 + num_evidence + num_evidence)
            if indexVal > 1:
                overallChange = addPoints(overallChange, -2, 'Low Information', art_num, art_sha256, art_id)

        if not (
                # 251e628c-2cd1-467a-9204-6f1b7c80cf79: T1.Q1.A6 Interview;
                # a2f97bce-2512-43e0-9605-0d137d30d8e6 T1.Q1.A3 Op-Ed
                # 0f15553b-95da-4eec-84f7-6809f5205ff2: T1.Q6.A5 Scientific study or discovery;
                # ad87bdb1-2247-4660-b0fd-64b19aa050fb T1.Q10.2 Report of what some person, body, or group said
            checkArtType(1,6, art_holistic) or checkArtType(1,3, art_holistic)  or
            checkArtType(6,5, art_holistic) or checkArtType(10,2, art_holistic)):  # T1.Q6.A5 and T1.Q10.2
            if (num_sources < 2 and num_evidence < num_assertions + num_args):
                overallChange = addPoints(overallChange, -2, 'Low Information', art_num, art_sha256, art_id)
    pointsdf = pd.concat([pointsdf, overallChange], axis=0, ignore_index=True)
    if reporting:
        pointsdf.to_csv(scoring_dir + '/AssessedPoints.csv')
    return pointsdf

def checkArtType(question_number, answer_number, holistic_df):
    if holistic_df == None:
        return False
    ques_df = holistic_df[holistic_df['question_Number'] == question_number]
    ans_df = ques_df[ques_df['agreed_Answer'] == answer_number]
    if len(ans_df):
        print("holi------------------scds57689988$%^&*^$%found match")
        return True
    return False


def get_indices_by_uuid(tua, tua_uuid):
    df = tua[tua['tua_uuid'] == tua_uuid]
    indices = []
    for i in range(len(df)):
        start = df['start_pos'].iloc[i]
        end = df['end_pos'].iloc[i]
        for n in range(start, end):
            indices.append(n)
    return indices


def get_dep_iaa(directory, schema='sources'):
    """

    :param directory: scoring directory, holds dep_iaa files
    :param schema: 'sources' or 'holistic' or ...
    :return: dataframe of the dep_s_ia fo the schema
    """
    if schema == 'sources' or schema == 'source':
        search_term = "ource"
    elif schema == 'holistic' or schema == 'overall':
        search_term = "olis"
    else:
        print("AAAHHHHH, can't evaluate get_dep_iaa in holistic_eval.py; directory:", directory, "schema:", schema)
    df  = None
    for root, dir, files in os.walk(directory):
        for file in files:
            print(file)
            if file.endswith('.csv'):
                if 'Dep_S_IAA' in file and search_term in file:
                    df = pd.read_csv(directory + '/' + file)
    if df == None:
        print("HOLISTIC EVAL, No specialist agreement for :", schema, "task")
        return None
    return df


def points_by_distance(value, target, scale, min=0, max=20):
    """
    finds points based on distance from target value.  Assumes value is in the wrong direction; ie if we want target of
    at least 4, value is 3.5; or if we want target of at most 5, value is 4.2
    can't go higher than the max
    Commonly, scale gets steeper for more extreme infractions
    """
    points = abs(target - value) * scale
    if points > max:
        return max
    return max(points, min) * -1


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
    if len(topical_tua) < 1:
        return 0
    # in current implementation highest case number is the # of cases; always starts at 1 counts up
    case_nums = topical_tua['case_number']
    return len(case_nums.unique())


def addPoints(df, points, label, art_num, art_sha, art_id, indices='[]'):
    df = df.append({'Schema': 'Holistic', 'points': points, 'Label': label, 'article_num': art_num,
                    'article_sha256': art_sha, 'article_id': art_id, 'highlighted_indices': indices}, ignore_index=True)
    return df

##___HOLDING RETIRED SCORING ALGS DOWN HERE
# check if low information
#        information_count = num_args + num_sources + num_evidence
#        information_index = information_count / article_size_index
#        # Guidance from spreadsheet has these values at -15 for <3 and -5 for <4; I'm hesitant to make it -15 until we
#        # make sure that case rarely occurs
#        if information_index < 3 and information_count < 5:
#            overallChange = addPoints(overallChange, -10, 'Very Low Information', art_num, art_sha256, art_id)
#        elif information_index < 4 and information_count < 8:
#            points = -5 * (4 - information_index)
#            overallChange = addPoints(overallChange, points, 'Low Information', art_num, art_sha256, art_id)

# check if article is assertion-happy--triager instruction is that it's only an assertion if it's a rogue claim
# not backed by anything in the article so these are bad
# assertion_index = num_assertions / article_size_index
# if assertion_index >= 5 and information_count < 5:
#     assertion_indices = getIndices(art_tua, 'Assertions')
#     overallChange = addPoints(overallChange, -12, 'Unsupported Assertions', art_num, art_sha256,art_id,
#                               indices=str(assertion_indices))
# elif assertion_index >= 2 and information_count < 8:
#     assertion_indices = getIndices(art_tua, 'Assertions')
#     points = -4*(assertion_index-2)
#     overallChange = addPoints(overallChange, points, 'Unsupported Assertions', art_num, art_sha256,art_id,
#                               indices=str(assertion_indices))

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
