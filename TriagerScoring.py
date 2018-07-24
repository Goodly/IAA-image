import numpy as np
from UnitizingScoring import *
from ThresholdMatrix import *
import pandas as pd
from math import floor

path1 = 'SemanticsTriager1.3C2-2018-07-19T17.csv'
path2 = 'FormTriager1.2C2-2018-07-19T17.csv'

def scoreTriager(starts,ends, users, numUsers, inFlags, length, globalExclusion):

    #TODO: do this for each category
    passers = findPassingIndices(starts, ends, numUsers, users, length)
    catExclusions = exclusionList(users, inFlags, minU = 4)
    flagExclusions = np.unique(np.append(globalExclusion,catExclusions))
    print('exclusions', flagExclusions)
    excl = findExcludedIndices(flagExclusions, users)
    #print(excl)
    if len(excl > 1):
        inFlags = exclude(excl, inFlags)
        users = exclude(excl, users)
        #ok to clip starts, ends because already know what passed
        starts, ends = exclude(excl,starts), exclude(excl, ends)
    codetoUser, userToCode= codeNameDict(users)
    coded = codeUsers(userToCode, users)
    #print(coded, numUsers)

    newStarts, newEnds = toStartsEnds(passers)
    #Exclude flags from users who didn't use case flags


    flags = determineFlags(starts, ends, newStarts, newEnds, coded, inFlags)
    print('Starts:',newStarts)
    print('Ends:',newEnds)
    print('Flags:', flags)
    print('---------------------------')
    return newStarts, newEnds,flags

def importData(path):
    data = pd.read_csv(path)
    article_nums = np.unique(data['task_pybossa_id'])

    for a in article_nums:
        print('---------------------------')
        art_data = data.loc[data['task_pybossa_id'] == a]
        annotator_count = len(np.unique(art_data['contributor_id']))
        users = art_data['contributor_id'].tolist()
        flags = art_data['case_number'].tolist()
        cats = art_data['topic_name'].tolist()
        flagExclusions = exclusionList(users, flags, cats)
        #print(flagExclusions)
        if annotator_count >= 2:
            cats = np.unique(art_data['topic_name'])
            for c in cats:

                cat_data = art_data.loc[art_data['topic_name'] == c]
                starts = [int(s) for s in cat_data['start_pos'].tolist()]
                ends = [int(e) for e in cat_data['end_pos'].tolist()]
                users = cat_data['contributor_id'].tolist()
                flags = cat_data['case_number'].tolist()
                length = floor(cat_data['source_text_length'].tolist()[0])
                numUsers = len(np.unique(users))
                print('//Article:', a, 'Category:', c, 'numUsers:', numUsers)
                scoreTriager(starts, ends, users, numUsers, flags, length, flagExclusions)

    print("DONE")

def findExcludedIndices(exclusions, users):
    #print(exclusions, users)
    indices = np.array(())
    for u in np.unique(users):
        if u in exclusions:
            uIndices = np.nonzero(users == u)
            #print(uIndices)
            indices = np.append(indices,uIndices)
    #print('indices', indices)
    return indices
def exclude(indices, arr):
    # print(flags, len(flags))
    # print('indices',indices)
    arr = np.array(arr)
    return np.delete(arr, indices)
def exclusionList(users, flags,cats = None, minU= 8):
    excluded = []
    for u in np.unique(users):
        myUserIndices = np.nonzero(users == u)[0]
        # print(myUserIndices)
        # print(np.array(users)[myUserIndices])
        oneCount = 0
        pot = 0
        score = 0
        #print(myUserIndices)
        for i in myUserIndices:
            #print(i)
            if cats!=None and cats[i]!= 'Language':
                if flags[i] == 1:
                    oneCount+=1
                pot = pot +1
            if pot>0:
                score = oneCount/pot
        if score>.8 and pot > minU:
            excluded.append(u)
    #print('excl', excluded,'users', np.unique(users))
    return excluded

def codeNameDict(users):
    uqUsers = np.sort(np.unique(users))
    codeDict = {}
    userDict = {}
    for i in range(len(uqUsers)):
        codeDict[i] = uqUsers[i]
        userDict[uqUsers[i]] = i
    return codeDict, userDict

def codeUsers(userDict, users):
    coded = []
    for u in users:
        coded.append(userDict[u])
    return coded

def findPassingIndices(starts, ends, numUsers, users, length):
    #print(starts)
    answerMatrix = toArray(starts, ends, length, numUsers, users, None)
    percentageArray = scorePercentageUnitizing(answerMatrix, length, numUsers)
    passersArray = np.zeros(len(percentageArray))
    # TODO: instead of passing to threshold matrix each time, just find out minScoretoPass
    for i in range(len(percentageArray)):
        if evalThresholdMatrix(percentageArray[i], numUsers, 1.4) == 'H':
            passersArray[i] = 1
    return passersArray

def toStartsEnds(passers):
    prev = 0
    starts = []
    ends = []
    for i in range(len(passers)):
        if passers[i] != prev:
            if prev == 0:
                starts.append(i)
            elif prev == 1:
                ends.append(i-1)
            prev = 1-prev
    if len(ends)<len(starts):
        ends.append[passers[-1]]
    return starts, ends

def toFlagMatrix(starts, ends, nStarts, nEnds, codedUsers, flags):
    if len(nStarts)>0 and len(np.unique(codedUsers)>0):
        flagMatrix = np.zeros((len(nStarts), len(np.unique(codedUsers))))
        #i corresponds tot he code of a user

        for i in np.arange(len(starts)):
            #print('i',i)
            for j in np.arange(len(nStarts)):
                #print(j)
                if (starts[i] < nStarts[j] and ends[i] > nStarts[j]) or \
                        (starts[i]< nEnds[j] and ends[i] > nEnds[j]):
                    flagMatrix[j][codedUsers[i]] = flags[i]
        return flagMatrix.T
    return []

def assignFlags(matrix):
    numUsers = len(matrix)
    numNStarts = len(matrix[0])
    currFlag = 1
    sortedNStarts = []
    flags = np.zeros(numNStarts)
    for i in range(numNStarts):
        if i not in sortedNStarts:
            sortedNStarts.append(i)
            flags[i] = currFlag
            currFlag = currFlag + 1
            for j in range(i, numNStarts):
                if j not in sortedNStarts:
                    score = 0
                    potential = 0
                    for u in range(numUsers):
                        if matrix[u][i] != 0 and matrix[u][j] != 0 :
                            potential += 1
                            if matrix[u][i] == matrix[u][j]:
                              score += 1
                    if potential > 0 and score/potential >= .5:
                        flags[j] = flags[i]
                        sortedNStarts.append(j)
    return flags


def determineFlags(starts, ends, nStarts, nEnds, codedUsers, flags):
    matrix = toFlagMatrix(starts, ends, nStarts,nEnds, codedUsers, flags)
    print(matrix)
    #print(matrix)
    if len(matrix)>0 and len(matrix[0]>0):
        outFlags = assignFlags(matrix)
        return outFlags
    return []


print("#####SEMANTICS TRIAGER AGREED UPON DATA!!!#####")
importData(path1)

print()
print()
print("#####FORM TRIAGER AGREED UPON DATA!!!#####")
importData(path2)
# s = [5, 45, 3, 80, 6, 65]
#
# e1 = [30,100, 30,100, 30,100]
# l = 120
# u = [4,4,7,7,3,3]
# f = [1,3,4,6,7,2]
# f2 = [1,1,4,4,7,7]
# c = 3

# scoreTriager(s,e1,l,u,3,f,c)
# scoreTriager(s,e1,l,u,3,f2,c)