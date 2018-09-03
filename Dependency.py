import math

import pandas as pd
import numpy as np
import os
from math import isnan
from dataV2 import create_dependencies_dict
from dataV2 import get_path
from dataV2 import readIndices

def calc_get_files_depenency(directory):
    schema = []
    iaa = []
    for root, dir, files in os.walk(directory):
        for file in files:
            if file.endswith('.csv') and 'Dep' not in file:
                print("Checking Agreement for "+directory+'/'+file)
                if 'S_IAA' in file:
                    iaa.append(directory+'/'+file)
                elif 'Schema' in file:
                    schema.append(directory+'/'+file)
    schema.sort()
    iaa.sort()
    assert(len(schema)==len(iaa))
    for i in range(len(schema)):
        print('launching with', schema[i], iaa[i])
        handleDependencies(schema[i], iaa[i])


def handleDependencies(schemaPath, iaaPath):
    schemData = pd.read_csv(schemaPath, encoding = 'utf-8')
    iaaData = pd.read_csv(iaaPath,encoding = 'utf-8')
    dependencies = create_dependencies_dict(schemData)
    print('haves a depend')
    tasks = np.unique(iaaData['task_uuid'].tolist())
    for t in tasks:
        iaaTask = iaaData[iaaData['task_uuid'] == t]
        #childQuestions
        for ch in dependencies.keys():
            print('newChild', ch)
            child = dependencies[ch]
            needsLove = checkNeedsLove(iaaTask, ch)
            if needsLove:
                print("INEEDAHERO")
                indices = np.zeros(0)
                alpha = np.zeros(0)
                alphainc = np.zeros(0)
                #check if this question even got a score
                iaaQ = iaaTask[(iaaTask['question_Number']) == (ch)]
                answers = iaaQ['agreed_Answer'].tolist()
                if len(answers)>0:
                    print("GOTANS")
                    print(answers)
                answers = find_real_answers(answers)
                print("WHERE")
                if len(answers)>0:
                    print("WOITYDOO")
                rows = find_index(iaaQ, answers, 'agreed_Answer')
                print(rows)
                if len(answers)>0:
                    #questions the child depends on
                    for par in child.keys():
                        print('newPar')
                        iaaPar = iaaTask[iaaTask['question_Number'] == (par)]
                        neededAnswers = child[par]
                        for ans in neededAnswers:
                            iaaparAns = iaaPar[iaaPar['agreed_Answer'] == str(ans)]
                            print(ans, iaaPar['agreed_Answer'].tolist())
                            print("ONELINEGUY")
                            print(iaaparAns)
                            if len(iaaparAns>0):
                                print("GOTONEMATEY")
                                newInds = iaaparAns['highlighted_indices'].tolist()
                                newInds = readIndices(newInds[0])
                                newAlph = iaaparAns['alpha_unitizing_score'].tolist()
                                newIncl = iaaparAns['alpha_unitizing_score_inclusive'].tolist()
                                for i in range(len(newInds)):
                                    print(newInds, newInds[i])
                                    indices = np.append(indices, newInds[i])
                                alpha = np.append(alpha, float(newAlph[0]))
                                alphainc = np.append(alphainc, float(newIncl[0]))
                                print('mjrpupdate')
                                print(indices)
                                print(alpha)
                indices = np.unique(indices).tolist()
                print(alpha)
                alpha = np.mean(alpha)
                alphainc = np.mean(alpha)
                print("FOR YOUR BOAT")
                print(rows)
                if len(rows)>0:
                    print("UCROSSRIVER")
                for row in rows:
                    print('doing Transfer')
                    iaaData.at[row, 'highlighted_indices'] = indices
                    iaaData.at[row, 'alpha_unitizing_score'] = alpha
                    iaaData.at[row, 'alpha_unitizing_score_inclusive'] = alphainc
                    print("PUPDATED")
                    print(iaaData.loc[row])
    print('exporting to csv')
    path, name = get_path(iaaPath)

    iaaData.to_csv(path+'Dep_'+name,  encoding = 'utf-8')

    print("Table complete")


def checkNeedsLove(df, qNum):
    qdf = df[df['question_Number'] == qNum]
    alphas = (qdf['alpha_unitizing_score'])
    for a in alphas:
        try:

            j = float(a)+1
            ans = math.isnan(j)
            return ans
        except:
            pass
    return True

def find_real_answers(answers):
    out = []
    for a in answers:
        if a.isdigit():
            out.append(int(a))
    return out


def find_index(df, targetVals,col):
    indices = []
    for v in targetVals:
        shrunk = df[df[col] == str(v)]
        print("SRK")
        print(shrunk)
        if len(shrunk)>0:
            inds = []
            for i in shrunk.index:
                inds.append(i)
            print("INDS")
            print(inds)
            for i in inds:
                indices.append(i)
    return indices

handleDependencies('./demo1/DemoLang-2018-09-01T2240-Schema.csv', './demo1/S_IAA_DemoLang-2018-09-01T2240-DataHuntHighlights.csv')
calc_get_files_depenency('./demo1')
