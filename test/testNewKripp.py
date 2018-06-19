import krippendorff
import numpy as np

def scoreAlphaUnitizing(starts,ends,length,numUsers,dFunc = 'nominal'):
    """takes in iterables starts,and ends as well as length of the document
    and the total number of Users who were asked to annotate """
    matrix = unitsToArray(starts,ends,length,numUsers)
    return score(matrix,distanceFunc = dFunc)

def score(answerMatrix, distanceFunc):
    """provides the krippendorff scores
    of the data passed in, distanceFunc should be
    'nominal', 'ordinal', 'interval', 'ratio' or a callable
    """

    return krippendorff.alpha(value_counts = answerMatrix, \
        level_of_measurement = distanceFunc)

def unitsToArray(starts, ends, length, numUsers):
    assert len
    col1= np.zeros(length)
    col2 = np.zeros(length)
    unitsMatrix = np.stack((col1,col2), axis = 0).T
    for i in range(length):
        unitsMatrix[i][1] = numUsers
    def raiseMatrix(start, end):
        for i in range(start, end):
            unitsMatrix[i][0] = unitsMatrix[i][0]+1
            unitsMatrix[i][1] = unitsMatrix[i][1]-1

    for i in range(len(starts)):
        raiseMatrix(starts[i],ends[i])
    print("Processed Matrix")
    print(unitsMatrix)
    return unitsMatrix




##TEST DATA below
matA = np.array([[3,0,0],[0,3,0],[0,0,3]])
matB = np.array([[1,2,0],[2,0,1],[0,0,3]])
#starts,ends,length,numUsers
sA = [1,4,8,1,2,9]
eA = [6,12,12,6,10,12]
lA = 22
nuA= 20

matC = unitsToArray(sA,eA,lA,12)
matD = unitsToArray(sA,eA,12,nuA)
