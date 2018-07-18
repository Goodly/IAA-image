import krippendorff
import numpy as np
from ThresholdMatrix import *

def scoreNuUnitizing(starts,ends,length,numUsers,users, userWeightDict, winner = 0, answers = 'x'):
    # Todo: resolve one user making overlapping highlights that skew data
    if answers == 'x':
        answers = np.zeros(len(users))
    answerMatrix = toArray(starts,ends,length,numUsers, users, userWeightDict)
    percentageArray = scorePercentageUnitizing(answerMatrix,length,numUsers)
    filteredData = filterSingular(percentageArray, answers,numUsers,users,starts,ends, winner)
    #f for filtered
    fStarts,fEnds,fNumUsers,goodIndices, fUsers = filteredData[0], filteredData[1], \
                                                  filteredData[2], filteredData[3], filteredData[4]
    if len(fStarts)==0:
        return 'L', 'L', 'L'
    filteredMatrix = toArray(fStarts, fEnds,length, fNumUsers, fUsers, userWeightDict)
    inclusiveMatrix = toArray(starts, ends, length, numUsers, users, userWeightDict)
    score = scoreAlpha(filteredMatrix, 'nominal')
    inclusiveScore = scoreAlpha(inclusiveMatrix, 'nominal')
    return score, inclusiveScore, goodIndices


def scoreAlphaUnitizing(starts,ends,length,numUsers,dFunc,users):
    """takes in iterables starts,and ends as well as length of the document
    and the total number of Users who were asked to annotate
    returns krippendorff unitizing score for the article, this method
    used mainly for testing and is not used in final algorithm for this"""
    matrix = toArray(starts,ends,length,numUsers, users)
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

def toArray(starts,ends,length,numUsers, users, userWeightDict):
    uniqueUsers = np.unique(np.array(users))
    userBlocks = np.zeros((int(numUsers), length))
    astarts, aends = np.array(starts), np.array(ends)
    for u in range(len(uniqueUsers)):
        indices = getIndicesFromUser(users, uniqueUsers[u])
        userStarts = astarts[indices]
        userEnds = aends[indices]
        for start in range(len(userStarts)):
            for i in range(userStarts[start], userEnds[start]):
                userBlocks[u][i] += 1
    #Now there are arrays of 1s and 0s, gotta collapse them
    #and make the possibilities column
    col1 = np.zeros(length)
    for userBlock in userBlocks:
        col1 = col1+userBlock
    col2 = np.zeros(length)
    for i in range(len(col2)):
        col2[i] = numUsers-col1[i]
    unitsMatrix = np.stack((col1, col2), axis=0).T
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
        if evalThresholdMatrix(percentageScoresArray[i], numUsers) == 'H':
            passingIndexes.append(i)
    majorityUsersUnique = getMajorityUsers(passingIndexes, users, starts, ends)
    goodIndices =getIndicesFromMajorityUsers(users, majorityUsersUnique)
    if  len(goodIndices)<1:
        return ([],[],0,[],[])
    starts, ends, users = np.array(starts), np.array(ends), np.array(users)

    starts = starts[goodIndices]
    ends = ends[goodIndices]
    users = users[goodIndices]
    numGoodUsers = len(users)
    out = [starts, ends, numGoodUsers, passingIndexes, users]
    return out

def getMajorityUsers(passingIndexes, users, starts, ends):
    """returns array of unique users who highlighted
    anything that passed the agreement threshold Matrix
    """
    majorityUsers = []
    for i in range(len(starts)):
        for j in range(starts[i], ends[i]):
            if j in passingIndexes:
                if users[i] not in majorityUsers:
                    majorityUsers.append(users[i])
    majorityUsers = np.array(majorityUsers)
    return majorityUsers


def filterIndexByAnswer(winner, answers):
    majorityIndices = np.nonzero(answers == winner)
    return majorityIndices

def getIndicesFromUser(users, majorityUser):
    """Takes in array of all users ordered
    the same as the starts and ends lists and an array
    of unique users who had an agreed upon highlight and
    returns array of all the indices that any user with
    an agreed upon highlight had highlighted """
    majorityIndices = np.nonzero(users == majorityUser)
    return majorityIndices


def getIndicesFromMajorityUsers(users,majorityUsers):
    """Takes in array of all users ordered
    the same as the starts and ends lists and an array
    of unique users who had an agreed upon highlight and
    returns array of all the indices that any user with
    an agreed upon highlight had highlighted """
    goodUserIndices = []
    for i in range(len(users)):
        if users[i] in majorityUsers:
            goodUserIndices.append(i)
    return np.array(goodUserIndices)

