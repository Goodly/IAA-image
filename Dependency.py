import math
import pandas as pd
import numpy as np
import os
import json
from dataV2 import *
def eval_dependency(directory, iaa_dir, out_dir = None):
    print("DEPENDENCY STARTING")
    if out_dir is None:
        out_dir = 'scoring_'+directory
    print('dir', directory, iaa_dir, out_dir)
    schema = []
    iaa = []
    for root, dir, files in os.walk(directory):
        for file in files:
            if file.endswith('.csv') and 'Dep' not in file:
                print("evaluating dependencies  for "+directory+'/'+file)
                if 'Schema' in file:
                    schema.append(directory+'/'+file)
    for root, dir, files in os.walk(iaa_dir):
        for file in files:
            if file.endswith('.csv') and 'Dep' not in file:
                print("evaluating dependencies for "+directory+'/'+file)
                if 'S_IAA' in file:
                    iaa.append(iaa_dir+'/'+file)

    schema.sort()
    iaa.sort()
    assert(len(schema)==len(iaa), 'mismatched files ', len(schema), 'schema', len(iaa), 'iaa oututs')
    out_dir = make_directory(out_dir)
    for i in range(len(schema)):
        handleDependencies(schema[i], iaa[i], out_dir)
    return out_dir

def handleDependencies(schemaPath, iaaPath, out_dir):
    schemData = pd.read_csv(schemaPath, encoding = 'utf-8')
    iaaData = pd.read_csv(iaaPath,encoding = 'utf-8')
    dependencies = create_dependencies_dict(schemData)
    print(schemaPath, "DEPENDENCIES DICS \n", dependencies)
    tasks = np.unique(iaaData['task_uuid'].tolist())
    iaaData['prereq_passed'] = iaaData['agreed_Answer']

    iaaData = iaaData.sort_values(['question_Number'])

    #filter out questions that should never of been asksed because no agreement on prerequisites
    for q in range(len(iaaData)):
        qnum = iaaData['question_Number'].iloc[q]
        ans = iaaData['agreed_Answer'].iloc[q]
        tsk = iaaData['task_uuid'].iloc[q]
        iaaData['prereq_passed'].iloc[q] = checkPassed(qnum, dependencies, iaaData, tsk, ans)
    iaaData = iaaData[iaaData['prereq_passed'] == True]

    iaaData = iaaData.sort_values("article_num")



    for t in tasks:
        iaaTask = iaaData[iaaData['task_uuid'] == t]
        #childQuestions
        for ch in dependencies.keys():

            child = dependencies[ch]
            needsLove = checkNeedsLove(iaaTask, ch)
            if needsLove:
                indices = np.zeros(0)
                alpha = np.zeros(0)
                alphainc = np.zeros(0)
                #check if this question even got a score
                iaaQ = iaaTask[(iaaTask['question_Number']) == (ch)]
                answers = iaaQ['agreed_Answer'].tolist()
                answers = find_real_answers(answers)
                rows = find_index(iaaQ, answers, 'agreed_Answer')
                validParent = False
                if len(answers)>0:
                    #questions the child depends on
                    for par in child.keys():
                        iaaPar = iaaTask[iaaTask['question_Number'] == (par)]
                        neededAnswers = child[par]

                        for ans in neededAnswers:
                            iaaparAns = iaaPar[iaaPar['agreed_Answer'] == ans]
                            if len(iaaparAns>0):
                                validParent = True
                                newInds = [get_indices_hard(ind) for ind in iaaparAns['highlighted_indices'].tolist()]
                                #newInds = parseList(newInds)
                                newAlph = iaaparAns['alpha_unitizing_score'].tolist()
                                newIncl = iaaparAns['alpha_unitizing_score_inclusive'].tolist()
                                for i in range(len(newInds)):
                                    indices = np.append(indices, newInds[i])
                                alpha = np.append(alpha, (newAlph[0]))
                                alphainc = np.append(alphainc, (newIncl[0]))
                #If parent didn't pass, this question should not of been asked
                if not validParent:
                    for row in rows:
                        iaaData.at[row,'agreed_Answer'] = -1
                        iaaData.at[row, 'coding_perc_agreement'] = -1
                indices = np.unique(indices).tolist()
                try:
                    alpha = alpha[0]
                    alphainc = alphainc[0]
                except IndexError:
                    alpha, alphainc = -1,-1

                for row in rows:
                    iaaData.at[row, 'highlighted_indices'] = json.dumps(indices)
                    iaaData.at[row, 'alpha_unitizing_score'] = alpha
                    iaaData.at[row, 'alpha_unitizing_score_inclusive'] = alphainc
    print('exporting to csv')
    path, name = get_path(iaaPath)

    iaaData.to_csv(out_dir+'Dep_'+name,  encoding = 'utf-8')

    print("Table complete")
    return out_dir

def parseList(iterable):
    out = []
    for i in range(len(iterable)):
        addendum = indicesFromString(iterable[i])
        out.append(addendum)
    return out
def checkNeedsLove(df, qNum):
    #Checks if the question's parent prompts users for a highlight
    qdf = df[df['question_Number'] == qNum]
    alphas = (qdf['alpha_unitizing_score'])
    #If no rows correspond to the child question
    if qdf.empty:
        return False
    for a in alphas:
        if not checkIsVal(a):
            return True
    return False

def checkPassed(qnum, dependencies, iaadata, task, answer):
    """
    checks if the question passed and if a prerequisite question passed
    """
    iaatask = iaadata[iaadata['task_uuid'] == task]
    qdata = iaatask[iaatask['question_Number'] == qnum]
    if not checkIsVal(answer):
        return False
    #print('keys', dependencies.keys())
    if qnum in dependencies.keys():
        #fprint("QNUM", qnum)
        #this loop only triggered if child question depends on a prereq
        for parent in dependencies[qnum].keys():
            #Can't ILOC because checklist questions have many answers
            pardata = iaatask[iaatask['question_Number'] == parent]
            parAns = pardata['agreed_Answer'].tolist()
            valid_answers = dependencies[qnum][parent]
            for v in valid_answers:
                #cast to string because all answers(even numeric) are read as strings and no conversion done
                strv = str(v)
                #Won't be found if it doesn't pass
                if strv in parAns:
                    par_ans_data = pardata[pardata['agreed_Answer'] == strv]
                    #print(len(par_ans_data['prereq_passed']), 'ppassed', par_ans_data['prereq_passed'])
                    #In case the parent's prereq didn't pass
                    if par_ans_data['prereq_passed'].iloc[0] == True:
                       return True
            return False
    return True


def checkIsVal(value):
    #returns true if value is a possible output from IAA that indicates the child q had user highlights
    if value == "M" or value == "L":
        return True
    #if its NAN
    if pd.isna(value):
        return False
    try:
        j = float(value) + 1
        ans = math.isnan(j)
        if ans:
            return False
        return True
    except:
        pass
    return False

def checkIsNum(value):
    #if its NAN
    if pd.isna(value):
        return False
    try:
        j = float(value) + 1
        ans = math.isnan(j)
        if ans:
            return False
        return True
    except:
        pass
    return False
def find_real_answers(answers):
    out = []
    for a in answers:
        if isinstance(a, int) or a.isdigit():
            out.append(int(a))
    return out


def find_index(df, targetVals,col):
    indices = []
    for v in targetVals:
        shrunk = df[df[col] == v]
        if len(shrunk)>0:
            inds = []
            for i in shrunk.index:
                inds.append(i)
            for i in inds:
                indices.append(i)
    return indices

#eval_depenency('./demo1')
