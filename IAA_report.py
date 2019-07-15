import os
import pandas as pd

from dataV2 import make_directory

def make_iaa_human_readable(iaa_dir, report_dir):
    print("making it readable")
    iaa = []
    for root, dir, files in os.walk(iaa_dir):
        for file in files:
            if file.endswith('.csv') and 'Dep' not in file:
                print("evaluating dependencies for "+iaa_dir+'/'+file)
                if 'S_IAA' in file:
                    iaa.append(iaa_dir+'/'+file)

    if len(iaa)>0:
        collapsed = pd.read_csv(iaa[0])
    else:
        print("NO WEIGHTS FOUND")
        return
    for i in range(1,len(iaa)):
        s_iaa = pd.read_csv(iaa[i])
        collapsed = collapsed.append(s_iaa)
    useful_cols = collapsed[['article_num', 'schema_namespace', 'question_Number', 'question_type',
                             'agreed_Answer', 'coding_perc_agreement', 'alpha_unitizing_score', 'agreement_score',
                             'num_users', 'num_answer_choices', 'target_text', 'question_text', 'answer_content']]
    make_directory(report_dir)
    useful_cols.to_csv(report_dir+'/'+'S_IAA_human_version')
