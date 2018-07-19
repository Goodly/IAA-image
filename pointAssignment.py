from UnitizingScoring import *
import numpy as np


sourceDatabase = {}
JournalistDatabase = {}
ArticleDatabase = {}

argValToWeightDict= {1:3, 2:2, 3:1, 4:.5, 5:1, 6:1}
sourceValToWeightDict= {1:2, 2:1, 3:.5, 4:.25, 5:.5, 6:.5, 7:.5}

#IMPORTANTNOTE: THIS ASSUMES pts reocmmended are positive, as in we subtract those points from 100 later!!!!

def assignPoints(ptsRec, ptsRecUnitization, sourceUnitization, argUnitization, argVal, sourceVal, article, journalist):
    doesPass, passingIndices = checkAgreement(ptsRecUnitization, sourceUnitization)
    if doesPass:
        print("IT'S A SOURCE")
        source = getSource(sourceUnitization)
        sendPoints(source, ptsRec, sourceDatabase)
        if checkSpecialCase(argVal, sourceVal, ptsRec, article, journalist) != 'NotSpecial':
            print("It's Special")
            return
        sourceMult = calcImportanceMultiplier(sourceVal, sourceValToWeightDict)
        sourceAdjustedValue = sourceMult*ptsRec
        argMult = calcArgImportanceMultiplier(argUnitization, ptsRecUnitization, argVal)
        sendArticleJournalistPoints(sourceAdjustedValue, argMult, article, journalist)
    else:
        argMult = calcArgImportanceMultiplier(argUnitization, ptsRecUnitization, argVal)
        sendArticleJournalistPoints(ptsRec, argMult, article, journalist)

def sendArticleJournalistPoints(ptsrec, multiplier, article, journalist):
    points = ptsrec*multiplier
    sendPoints(article, points, ArticleDatabase)
    sendPoints(journalist, points, JournalistDatabase)
def checkSpecialCase(argVal, sourceVal, ptsRec, article, journalist):
    if argVal == 5 and (sourceVal == 5 or sourceVal == 6 or sourceVal == 7):
        multiplier = -1
        sendArticleJournalistPoints(ptsRec, multiplier, article, journalist)
        return
    elif argVal == 2:
        sendArticleJournalistPoints(7, 1, article, journalist)
        return
    else:
        return 'NotSpecial'

def calcImportanceMultiplier(value, dict):
    return dict[value]

def calcArgImportanceMultiplier(argUnitization, ptsRecUnitization, argVal):
    doesPass, passingIndices = checkAgreement(ptsRecUnitization, argUnitization)
    if doesPass:
        return calcImportanceMultiplier(argVal, argValToWeightDict)
    else:
        return 1
def checkAgreement(arr1, arr2, threshold = .9):
    """arr1 and arr2 are lists of every unitization
    Raw score might be best indicator, highest percentage of aunits in agreement with either of the unitizaitons"""
    length = max(max(arr1), (max(arr2)))+1

    answerMatrix = indicesToMatrix(arr1, arr2, length)
    percentageArray = np.array(scorePercentageUnitizing(answerMatrix, length, 2))
    passingIndices = np.nonzero(percentageArray == 1)[0]
    numPasses = len(passingIndices)
    rawScore = max((numPasses/len(arr1), numPasses/len(arr2)))
    doesPass = rawScore > threshold
    return doesPass, passingIndices

def indicesToMatrix(arr1, arr2, length):
    """converts lists of the indices of unitizations to an answer matrix"""
    col1 = np.zeros(length)
    col2 = np.zeros(length)
    col1[arr1] = 1
    col2[arr2] = 1
    together = col1+col2
    unTogether = 2-together
    matrix = np.stack((together, unTogether),axis = 0).T
    return matrix



def sendPoints(target, points, targetDatabase):
    if target in targetDatabase.keys():
        targetDatabase[target] = targetDatabase[target]+points
    else:
        targetDatabase[target] = points
def getSource(sourceUnitizaiton):
    return 0

print(checkAgreement([1,2,3,4], [1,2,3,4]))

u1 = [3,4,5,6,7,8,9,10]
u2 = [6,7,8,9,10,11,12,13]
u3 = [1,2,3,4,5,6]
u4 = [17,18,19,20,21]

assignPoints(10,u1,u1,u1,3, 3, 1, 'bill')
print('source', sourceDatabase)
print('journalists', JournalistDatabase)
print('articles', ArticleDatabase)
assignPoints(10,u1,u1,u4,3,3,2, 'bill')
print('source', sourceDatabase)
print('journalists', JournalistDatabase)
print('articles', ArticleDatabase)
assignPoints(10,u1,u4,u4,3,3,2, 'bill')
print('source', sourceDatabase)
print('journalists', JournalistDatabase)
print('articles', ArticleDatabase)
assignPoints(10,u4,u4,u4,5,5,2, 'bill')
print('source', sourceDatabase)
print('journalists', JournalistDatabase)
print('articles', ArticleDatabase)