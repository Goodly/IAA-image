import numpy as np
import pandas as pd
import os


def launch_Weighting(directory):
    print("WEIGHTING STARTING")
    iaaFiles = []
    print('weightdir',directory)
    for root, dir, files in os.walk(directory):
        for file in files:
            print(file)
            if file.endswith('.csv'):
                if 'Dep_S_IAA' in file:
                    print('gotaFile', file)
                    iaaFiles.append(directory+'/'+file)
    print('files', iaaFiles)
    for f in iaaFiles:
        weighting_alg(f, './config/weight_key.csv', './config/weight_key_scaling_guide.csv', directory)

def weighting_alg(IAA_csv_file, credibility_weights_csv_file, weight_scale_csv, directory = './'):

    IAA_csv = pd.read_csv(IAA_csv_file)
    #IndexError when the csv is empty
    try:
        IAA_csv_schema_name = IAA_csv.schema_namespace.iloc[0]
    except IndexError:
        if IAA_csv.shape[0]<1:
            return
        else:
            print(len(IAA_csv))
            print(IAA_csv)
            raise Exception('EricIsAnIdiotError')

    print('schemnam',IAA_csv_schema_name)
    if "uage" in IAA_csv_schema_name:
        IAA_csv_schema_type = "Language"
    elif "Reason" in IAA_csv_schema_name:
        IAA_csv_schema_type = "Reasoning"
    elif "Evidence" in IAA_csv_schema_name:
        IAA_csv_schema_type = "Evidence"
    elif "Probability" in IAA_csv_schema_name:
        IAA_csv_schema_type = "Probability"
    elif 'olistic' in IAA_csv_schema_name:
        IAA_csv_schema_type = "Holistic"
    else:
        print("unweighted IAA", IAA_csv_file, "aborting")
        return
    print("WEIGHINGWITHSCHEMA", IAA_csv_schema_type, IAA_csv_file)


    #don't need to check for this, it won't ever be matched with an answer weight
    # IAA_csv = IAA_csv.loc[IAA_csv.agreed_Answer!='U']
    # IAA_csv = IAA_csv.loc[IAA_csv.agreed_Answer!='M']
    # IAA_csv = IAA_csv.loc[IAA_csv.agreed_Answer!='L']

    IAA_csv = IAA_csv.rename(columns={ "question_Number": "Question_Number", 'agreed_Answer': 'Answer_Number'})
    IAA_csv['Schema'] = IAA_csv_schema_type
    credibility_weights_csv = pd.read_csv(credibility_weights_csv_file)
    weight_scale_table = pd.read_csv(weight_scale_csv)



    q6_points = 0
    # if IAA_csv_schema_type == "Evidence":
    #     if 6 in IAA_csv.column("Question_Number"):
    #
    #         question_six_table = IAA_csv.where("Question_Number", are.equal_to(6))
    #         q6_holder_points = 0
    #         a = "Correlation"
    #         b = "Cause precedes effect"
    #         c = "The correlation appears across multiple independent contexts"
    #         d = "A plausible mechanism is proposed"
    #         e = "An experimental study was conducted (natural experiments OK)"
    #         f = "The bigger the cause, the bigger the effect (dose response curve)"
    #         g = "Experts are cited"
    #         h = "Other evidence"
    #         i = "No evidence given"
    #
    #         for row in question_six_table.rows:
    #             if row.item("answer_content") == a or row.item("answer_content") == b or row.item("answer_content") == d:
    #                 q6_holder_points += row.item("agreement_score") * 50
    #             if row.item("answer_content") == c or row.item("answer_content") == e or row.item("answer_content") == f:
    #                 q6_holder_points += row.item("agreement_score") * 10
    #             if row.item("answer_content") == g or row.item("answer_content") == h:
    #                 q6_holder_points += row.item("agreement_score") * 1
    #
    #         q6_points = weighted_q6(q6_holder_points)

    IAA_csv["Question_Number"] = IAA_csv["Question_Number"].apply(int)

    IAA_csv['Answer_Number'] = IAA_csv['Answer_Number'].apply(convertToInt)
    for_visualization = pd.DataFrame()
    #uncomment when we want to scale question scores based on answers to other questions
    for task in np.unique(IAA_csv['quiz_task_uuid']):
        task_IAA = IAA_csv[IAA_csv['quiz_task_uuid'] == task]
        scaled_cred_weights = scale_weights_csv(credibility_weights_csv, weight_scale_table, task_IAA,
                                                    IAA_csv_schema_type)

    new_csv = pd.merge(scaled_cred_weights, IAA_csv, on =["Schema", "Question_Number", 'Answer_Number'])

    points = new_csv["Point_Recommendation"] * new_csv["agreement_score"]
    new_csv = new_csv.assign(agreement_adjusted_points = points)
    for_visualization = for_visualization.append(new_csv)


    column_names = ["article_num", "article_sha256", "article_id", "quiz_task_uuid", "Question_Number", "agreed_Answer",
                    "highlighted_indices", "Point_Recommendation", "agreement_adjusted_points", "Label", "target_text"]

    # if IAA_csv_schema_type == "Evidence":
    #     for_visualization.loc['Quality of evidence', 'agreement_adjusted_points'] = q6_points

    for_visualization['schema'] = pd.Series(IAA_csv_schema_type for i in range(len(for_visualization['article_sha256'])+1))
    for_visualization = for_visualization.loc[:, ~for_visualization.columns.duplicated()]
    out_file = directory+"/Point_recs_"+IAA_csv_schema_type+".csv"
    print(out_file)
    for_visualization.to_csv(out_file, encoding = 'utf-8')
    # You can choose to specify the path of the exported csv file in the .to_csv() method.
def weighted_q6(num):
    if num >= 160:
        score = 0
    elif 150 <= num < 160:
        score = 0.5
    elif 100 <= num <150:
        score = 2
    elif 50 <= num <100:
        score = 3
    elif num < 50:
        score = 4
    else:
        score = 5
    return score

def scale_weights_csv(weight_df, scale_df, iaa_df, schema):
    '''

    :param weight_df: weight_key
    :param scale_df: weight_scale_key
    :return: scaled weights dataframe
    '''
    if schema not in scale_df['if_schema']:
        return weight_df
    weight_df = weight_df[weight_df['Schema'] == schema]
    scale_df = scale_df[scale_df['if_schema'==schema]]
    scaled = weight_df
    for a in scale_df['if_ans_uuid']:
        #Gotta make this not be uuid, not stable enough, for now its fine cuase this isn't used
        if a in iaa_df['answer_uuid']:
            row = iaa_df[iaa_df['answer_uuid' == a]]
            #guaranteed to only happen once
            q = int(row['question_Number'].iloc[0])
            a = convertToInt(row['agreed_Answer'])
            mulrow = scale_df[scale_df['if_ans_uuid'] == a]
            mul = mulrow['mult'].iloc[0]
            scaled.loc[['Question_Number' == q, 'Answer_Number' == a, ['Point_Recommendation']]] = \
                scaled.loc[['Question_Number' == q, 'Answer_Number' == a, ['Point_Recommendation']]]*mul
    return scaled







def convertToInt(string):
    try:
        out = int(string)
        return out
    except:
        return -1

launch_Weighting('scoring_covid')