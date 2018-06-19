import krippendorff
import numpy as np

def scoreNickUnitizing(starts,ends,length,numUsers,users, dFunc = 'nominal'):
    answerMatrix = unitsToArray(starts,ends,length,numUsers)
    #print('answersMatrix')
    #print(answerMatrix)
    percentageArray = scorePercentageUnitizing(answerMatrix,length,numUsers)
    #print(percentageArray)
    filteredData = filterPassFail(percentageArray, answerMatrix,numUsers,users,starts,ends)
    #f for filtered
    fStarts,fEnds,fNumUsers =filteredData[0], filteredData[1], filteredData[2]
    filteredMatrix = unitsToArray(fStarts, fEnds,length, fNumUsers)
    #print(Filteredmatrix)
    #print('filtered matrix')
    ##print(filteredMatrix)
    print(np.array_equiv(answerMatrix, filteredMatrix))
    score = scoreAlpha(filteredMatrix, dFunc)
    return score


def scoreAlphaUnitizing(starts,ends,length,numUsers,dFunc):
    """takes in iterables starts,and ends as well as length of the document
    and the total number of Users who were asked to annotate
    returns krippendorff unitizing score for the article, this method
    used mainly for testing and is not used in final algorithm for this"""
    matrix = unitsToArray(starts,ends,length,numUsers)
    return scoreAlpha(matrix,distanceFunc = dFunc)

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
    for i in range(len(starts)-1):
        raiseMatrix(starts[i],ends[i])
    #print("Processed Matrix")
    #print(unitsMatrix)
    return unitsMatrix

def filterPassFail(percentageScoresArray, answerMatrix,numUsers,users,starts,ends):
    """
    filters the data so that only users who highlighted units that passed the
    thresholdmatrix after their percentage agreement was calculated get scored
    by the krippendorff unitizing measurement
    output is tuple(starts,ends,numGoodUsers)
    """
    passingIndexes = []
    print('max of percScores')
    print(np.max(percentageScoresArray))
    for i in range(len(percentageScoresArray)):
        #TODO: develop functional threshold matrix for more robust analysis
        if percentageScoresArray[i]>.4:
            passingIndexes.append(i)
        #if it failsor needs more, for now doing nothing,
        #TODO:add that funcitonality to here
        #fornow, just going to return the array of scores of passing indexes
    print('passingIndices')
    #print(passingIndexes)
    goodUsers = getGoodUsers(passingIndexes, users, starts, ends)
    print('users')
    print(goodUsers)
    goodIndices =getGoodIndices(users,goodUsers)
    if  len(goodIndices)<1:
        return ([],[],0)
    starts, ends = np.array(starts), np.array(ends)
    numGoodUsers = len(goodUsers)
    print(goodIndices)
    starts = starts[goodIndices]
    ends =ends[goodIndices]
    return starts,ends,numGoodUsers

def getGoodUsers(passingIndexes, users, starts, ends):
    goodDogs = []
    for i in range(len(starts)):
        if users[i] not in goodDogs:
            for j in range(starts[i], ends[i]):
                if j in passingIndexes:
                    goodDogs.append(users[i])
    #vprint('goodDog')
    #print(goodDogs)
    goodDogs = np.array(goodDogs)
    goodDogs = np.unique(goodDogs)
    return goodDogs

def getGoodIndices(users,goodDogs):
    goodUserIndices = []
    for i in range(len(users)):
        if users[i] in goodDogs:
            goodUserIndices.append(i)
    print('GoodDogIndices')
    print(goodUserIndices)
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
