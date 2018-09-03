from UnitizingScoring import *
import numpy as np
import pandas as pd
import os
from dataV2 import readIndices
sourceDatabase = {}
JournalistDatabase = {}
ArticleDatabase = {}

argValToWeightDict= {1:3, 2:2, 3:1, 4:.5, 5:1, 6:1}
sourceValToWeightDict= {1:2, 2:1, 3:.5, 4:.25, 5:.5, 6:.5, 7:.5}

#IMPORTANTNOTE: THIS ASSUMES pts reocmmended are positive, as in we subtract those points from 100 later!!!!
def assignPoints(directory):
    sourceFile, argRelevanceFile, weightFile = getFiles(directory)
    dataDict = storeData(sourceFile, argRelevanceFile, weightFile)
    articles = dataDict.keys()
    for art in articles:
        argAnswers, sourceAnswers = getArgAnswers(dataDict, art), getSourceAnswers(dataDict, art)
        argIndices, sourceIndices = getArgIndices(dataDict, art), getSourceIndices(dataDict, art)
        weightQ, weightA = getweightQA(dataDict, art)
        pointRecs = getpointRec(dataDict, art)
        weightInds = getweightIndices(data, article)

        #TODO: get labelname, weightingindices, weight, question/answer combos from Sam
        #can't just do questions cause some questions have more than one answer (checklist)


def storeData(sourceFile, argRelFile, weightFile):
    sourceData = pd.read_csv(sourceFile)
    argData = pd.read_csv(argRelFile)
    weightData = pd.read_csv(weightFile)
    #by articles not by tasks
    #TODO: change this to article_sha256 after it works
    #Use article not tasks, finding which task best fits the weighting recommenation
    uqArticles = np.unique(argData['article_num'])
    bigDict = {}
    for art in uqArticles:
        artArgData = argData[argData['article_num'] == art]
        argAnswers, argIndices = getAnswersIndices(artArgData)
        artSourceData = sourceData[sourceData['article_num'] == art]
        #there's many questions, only q 4 is relevant
        artQSourceData = artSourceData[artSourceData['question_Number'] == 4]
        sourceAnswers, sourceIndices = getAnswersIndices(artQSourceData)
        artWeights = weightData[weightData['article_num'] == art]
        labels = artWeights['Label'].tolist()
        weightInds = artWeights['highlighted_indices'].tolist()
        weightRec = artWeights['Point_Recommendation'].tolist()
        weightQs = artWeights['Question_Number'].tolist()
        weightAnswers = artWeights['Answer_Number'].tolist()
        bigDict[art] = {
            'argAnswers':argAnswers,
            'argIndices': argIndices,
            'sourceAnswers':sourceAnswers,
            'sourceIndices':sourceIndices,
            'labels':labels,
            'weightIndices': weightInds,
            'pointRec': weightRec,
            'weightQuestions':weightQs,
            'weightAnswers': weightAnswers
        }
    return bigDict
def getweightQA(data, article):
    return data[article]['weightQuestions'], data[article]['weightAnswers']
def getpointRec(data, article):
    return data[article]['pointRec']
def getweightIndices(data,article):
    indices = data[article]['weightIndices']
    filtered = [readIndices(ind) for ind in indices]
    return filtered

def getLabels(data, article):
    return data[article]['labels']
def getArgAnswers(data, article):
    return data[article]['argAnswers']


def getArgIndices(data, article):
    return data[article]['argIndices']


def getSourceAnswers(data, article):
    return data[article]['sourceAnswers']


def getSourceIndices(data, article):
    return data[article]['sourceIndices']


def strLstToIntLst(string):
    out = []
    num = None
    for i in range(len(string)):
        if string[i].isdigit():
            if num:
                num = num*10
                num = num+int(string[i])
            else:
                num = int(string[i])
        else:
            if num:
                out.append(num)
                num = None
    return out


def getAnswersIndices(artData):
    indices = np.array(artData['highlighted_indices'].tolist())
    answers = np.array(artData['agreed_Answer'].tolist())
    passingVals = findNumVals(answers)
    indices = indices[passingVals]
    answers = answers[passingVals]
    indices = [strLstToIntLst(ind) for ind in indices]
    return answers, indices


def getFiles(directory):
    #NEEDS: WeightingOutputs, sourceTriagerIAA, arg Source IAA
    sourceFile = None
    argRelevanceFile = None
    weightOutputs = None
    for root, dir, files in os.walk(directory):
        for file in files:
            print(file)
            if 'Dep_S_IAA' in file:
                print('siaa file-------------', file)
            if file.endswith('.csv')  in file and 'Quo' in file:
                print("found Sources File" + directory + '/' + file)
                sourceFile = directory+'/'+file
            if file.endswith('.csv')  in file and 'Arg' in file:
                print('Found Arguments File '+ directory+'/' + file)
                argRelevanceFile = directory+'/'+file
            if file.endswith('.csv')  in file and 'Point' in file:
                print('Found Arguments File '+ directory+'/' + file)
                argRelevanceFile = directory+'/'+file
    return sourceFile, argRelevanceFile, weightOutputs


def findNumVals(lst):
    indices = []
    for i in range(len(lst)):
        if lst[i].isdigit():
            indices.append(i)

    return indices


def findBestMatch(ptsUnits, modUnits):
    """
    :param ptsUnits: one list of passing units
    :param modUnits: list of lists of units of the modifier
    :return: index of the best modifier Unit
    """
    bestInd = 0
    bestScore = 0
    for i in range(len(modUnits)):
        score, units = calcOverlap(modUnits[i], ptsUnits)
        if score>bestScore:
            bestScore = score
            bestInd = i

    return bestInd


def assignPoints(ptsRec, ptsRecUnitization, sourceUnitization, argUnitization, argVal, sourceVal, article, journalist):
    """

    :param ptsRec:
    :param ptsRecUnitization: list of every index that was from the pointrec
    :param sourceUnitization: list of eveyr index that's a source
    :param argUnitization: list of eveyr index that's an arg
    :param argVal: the answer to the question about this
    :param sourceVal:
    :param article:
    :param journalist:
    :return:
    """
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
    rawScore, passingIndices = calcOverlap(arr1, arr2)
    doesPass = rawScore > threshold
    return doesPass, passingIndices


def calcOverlap(arr1, arr2):
    length = max(max(arr1), (max(arr2))) + 1

    answerMatrix = indicesToMatrix(arr1, arr2, length)
    percentageArray = np.array(scorePercentageUnitizing(answerMatrix, length, 2))
    passingIndices = np.nonzero(percentageArray == 1)[0]
    numPasses = len(passingIndices)
    rawScore = max((numPasses / len(arr1), numPasses / len(arr2)))
    return rawScore, passingIndices


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
source,args,weight = getFiles('./demo1')
data = (storeData(source,args,weight))
print(data)