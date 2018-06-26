import krippendorff
import numpy as np
from ThresholdMatrix import *

def scoreNickUnitizing(starts,ends,length,numUsers,users, winner = 0, answers = 'x'):
    if answers == 'x':
        answers = np.zeros(len(users))
    answerMatrix = unitsToArray(starts,ends,length,numUsers)
    percentageArray = scorePercentageUnitizing(answerMatrix,length,numUsers)
    filteredData = filterSingular(percentageArray, answers,numUsers,users,starts,ends, winner)
    #f for filtered
    fStarts,fEnds,fNumUsers,goodIndices = filteredData[0], filteredData[1], filteredData[2], filteredData[3]
    if len(fStarts)==0:
        return 'L', 'L'
    filteredMatrix = unitsToArray(fStarts, fEnds,length, fNumUsers)
    score = scoreAlpha(filteredMatrix, 'nominal')
    return score, goodIndices


def scoreAlphaUnitizing(starts,ends,length,numUsers,dFunc):
    """takes in iterables starts,and ends as well as length of the document
    and the total number of Users who were asked to annotate
    returns krippendorff unitizing score for the article, this method
    used mainly for testing and is not used in final algorithm for this"""
    matrix = unitsToArray(starts,ends,length,numUsers)
    return scoreAlpha(matrix, distanceFunc = dFunc)

def scoreAlpha(answerMatrix, distanceFunc):
    """provides the krippendorff scores
    of the data passed in, distanceFunc should be
    'nominal', 'ordinal', 'interval', 'ratio' or a callable
    """

    return krippendorff.alpha(value_counts = answerMatrix, \
        level_of_measurement = distanceFunc)

def scorePercentageUnitizing(answerMatrix,length,numUsers):
    """takes in iterables starts,and ends as well as length of the document
    and the total number of Users who were asked to annotate
    returns array of percentage agreement each character"""
    totalNumUsers = numUsers
    PercentScoresArray = np.zeros(length)
    for i in range(len(answerMatrix)):
        PercentScoresArray[i] = answerMatrix[i][0]/totalNumUsers
    return PercentScoresArray


def unitsToArray(starts, ends, length, numUsers):
    def raiseMatrix(start, end):
        for i in range(start, end):
            unitsMatrix[i][0] = unitsMatrix[i][0]+1
            unitsMatrix[i][1] = unitsMatrix[i][1]-1
    col1= np.zeros(length)
    col2 = np.zeros(length)
    unitsMatrix = np.stack((col1,col2), axis = 0).T
    for i in range(length):
        unitsMatrix[i][1] = numUsers
    for i in range(len(starts)):
        raiseMatrix(starts[i],ends[i])
    return unitsMatrix


def filterSingular(percentageScoresArray, answers, numUsers,users,starts,ends, winner):
    """
    filters the data so that only users who highlighted units that passed the
    thresholdmatrix after their percentage agreement was calculated get scored
    by the krippendorff unitizing measurement
    Used when users select a single answer choice
    output is tuple(starts,ends,numGoodUsers)
    """
    passingIndexes = []
    for i in range(len(percentageScoresArray)):
        #TODO: develop functional threshold matrix for more robust analysis
        if evalThresholdMatrix(percentageScoresArray[i], numUsers) == 'H':
            passingIndexes.append(i)
    goodUsers = getGoodUsers(passingIndexes, users, starts, ends)
    goodIndices =getGoodIndices(users, goodUsers, answers, winner)
    if  len(goodIndices)<1:
        return ([],[],0,[])
    starts, ends = np.array(starts), np.array(ends)
    numGoodUsers = len(goodUsers)
    starts = starts[goodIndices]
    ends = ends[goodIndices]
    return starts, ends, numGoodUsers, passingIndexes

def filterMultiple(percentageScoresArray, answerMatrix,numUsers,users,starts,ends, winner):
    """
    filters the data so that only users who highlighted units that passed the
    thresholdmatrix after their percentage agreement was calculated get scored
    by the krippendorff unitizing measurement
    Used when users select multiple answer choices, differs from method for
    singular answer choices by only incorporating data from each user for
    the answer choice they chose
    output is tuple(starts,ends,numGoodUsers)
    """
    passingIndexes = []
    print('percScoreArraylength', len(percentageScoresArray))
    for i in range(len(percentageScoresArray)):
        # TODO: develop functional threshold matrix for more robust analysis
        if evalThresholdMatrix(percentageScoresArray[i], numUsers) == 'H':
            passingIndexes.append(i)
    indices = filterIndexByAnswer
def getGoodUsers(passingIndexes, users, starts, ends):
    """returns array of unique users who highlighted
    anything that passed the agreement threshold Matrix
    """
    goodDogs = []
    for i in range(len(starts)):
        if users[i] not in goodDogs:
            for j in range(starts[i], ends[i]):
                if j in passingIndexes:
                    goodDogs.append(users[i])
    goodDogs = np.array(goodDogs)
    goodDogs = np.unique(goodDogs)
    return goodDogs


def filterIndexByAnswer(winner, answers):
    goodIndices = []
    for i in range(len(answers)):
        if answers[i]==winner:
            goodIndices.append(i)
    return np.array(goodIndices)


def getGoodIndices(users,goodDogs, answers, winner):
    """Takes in array of all users ordered
    the same as the starts and ends lists and an array
    of unique users who had an agreed upon highlight and
    returns array of all the indices that any user with
    an agreed upon highlight had highlighted """
    goodUserIndices = []
    for i in range(len(users)):
        if users[i] in goodDogs and answers[i] == winner:
            goodUserIndices.append(i)
    return np.array(goodUserIndices)




##TEST DATA below
matA = np.array([[3,0,0],[0,3,0],[0,0,3]])
matB = np.array([[1,2,0],[2,0,1],[0,0,3]])
#starts,ends,length,numUsers
sA = [1,4,8,1,2,9]
eA = [6,12,12,6,10,12]
lA = 22
uA = [1,2,3,4,1,2]
nuA= 20

matC = unitsToArray(sA,eA,lA,12)
matD = unitsToArray(sA,eA,12,nuA)
