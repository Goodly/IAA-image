import numpy as np
from UnitizingScoring import *
from ThresholdMatrix import *

def scoreTriager(starts,ends, length, users, numUsers, inFlags, categories):



    #TODO: do this for each category
    passers = findPassingIndices(starts, ends, length, numUsers, users)
    codetoUser, userToCode= codeNameDict(users)
    coded = codeUsers(userToCode, users)
    newStarts, newEnds = toStartsEnds(passers)
    flags = determineFlags(starts, ends, newStarts, newEnds, coded, inFlags)
    print(newStarts, newEnds, flags)
    return 0


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

def findPassingIndices(starts, ends, length, numUsers, users):
    answerMatrix = toArray(starts, ends, length, numUsers, users, None)
    percentageArray = scorePercentageUnitizing(answerMatrix, length, numUsers)
    passersArray = np.zeros(len(percentageArray))
    # TODO: instead of passing to threshold matrix each time, just find out minScoretoPass
    for i in range(len(percentageArray)):
        if evalThresholdMatrix(percentageArray[i], numUsers) == 'H':
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
    return starts, ends

def toFlagMatrix(starts, ends, nStarts, nEnds, codedUsers, flags):
    """returns a dictionary that has the new starts as the keys, and a list of every index of user that had a highlight
    overlap the agreed upon unitization """
    def addToStartsIndex(start, index):
        if start not in startsUsersDict.keys():
            startsUsersDict[start] = [(index, index)]
        else:
            startsUsersDict[start] = startsUsersDict[start].append(index)

    startsUsersDict = {}
    flagMatrix = np.zeros((len(nStarts), len(np.unique(codedUsers))))
    #i corresponds tot he code of a user
    for i in np.arange(len(starts)):
        for j in np.arange(len(nStarts)):
            if (starts[i] < nStarts[j] and ends[i] > nStarts[j]) or \
                    (starts[i]< nEnds[j] and starts[i] > nStarts[j]):
                flagMatrix[j][codedUsers[i]] = flags[i]
    return flagMatrix.T

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
                        if matrix[u][i] != 0 and matrix[u][j] != 0:
                            potential += 1
                        if matrix[u][i] == matrix[u][j]:
                            score += 1
                    if score/potential >= .5:
                        flags[j] = flags[i]
                        sortedNStarts.append(j)
    return flags


def determineFlags(starts, ends, nStarts, nEnds, codedUsers, flags):
    matrix = toFlagMatrix(starts, ends, nStarts,nEnds, codedUsers, flags)
    outFlags = assignFlags(matrix)
    return outFlags

s = [5, 45, 3, 80, 6, 65]

e1 = [30,100, 30,100, 30,100]
l = 120
u = [4,4,7,7,3,3]
f = [1,3,4,6,7,2]
f2 = [1,1,4,4,7,7]
c = 3

scoreTriager(s,e1,l,u,3,f,c)
scoreTriager(s,e1,l,u,3,f2,c)