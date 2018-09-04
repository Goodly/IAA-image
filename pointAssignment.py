from UnitizingScoring import *
import numpy as np
import pandas as pd
import os
import ast
from dataV2 import printType
from dataV2 import get_indices_hard
from dataV2 import indicesFromString
import csv
import json
from dataV2 import readIndices
sourceDatabase = {}
JournalistDatabase = {}
ArticleDatabase = {}

#-1 is a default value,
argValToWeightDict= {1:3, 2:2, 3:1, 4:.5, 5:1, 6:1, -1:1}
sourceValToWeightDict= {1:2, 2:1, 3:.5, 4:.25, 5:.5, 6:.5, 7:.5, -1:1}

#IMPORTANTNOTE: THIS ASSUMES pts reocmmended are positive, as in we subtract those points from 100 later!!!!


def pointSort(directory):
    print("SORTING STARTING")
    sourceFile, argRelevanceFile, weightFile = getFiles(directory)

    print(weightFile)
    outData = [['Article ID', 'Credibility Indicator ID ', 'Credibilty Indicator Category',
                'Credibility Indicator Name',
                'Points', 'Indices of Label in Article', 'Start', 'End']]
    artNum = 0000
    for weightSet in weightFile:
        print(weightSet)
        dataDict = storeData(sourceFile, argRelevanceFile, weightSet, './demo1/allTUAS.csv')
        articles = dataDict.keys()
        mergeWeightFiles(weightFile)
        for art in articles:

                print("WIPEDOUT")

                counter= 0
                artNum = retrieveArtNum(dataDict, art)
                argDic = retrieveArgDict(dataDict, art)
                sorcDic = retrieveSourceDict(dataDict, art)
                print(sorcDic)
                weightQ, weightA = getweightQA(dataDict, art)
                pointRecs = getpointRec(dataDict, art)
                weightInds = getweightIndices(dataDict, art)
                labels = getLabels(dataDict,art)
                schema =getSchema(dataDict, art)
                print("SCHEMING")
                for i in range(len(pointRecs)):
                    #print("ONSTEP", i)
                    wu = weightInds[i]
                    if isinstance(wu, str):
                        wu = get_indices_hard(wu)
                    bestSourceTask = findBestMatch(wu, sorcDic)
                    bestArgTask = findBestMatch(wu, argDic)
                    ptsRec = pointRecs[i]
                    print('PREC', ptsRec)
                    print(labels[i])
                    print(schema)
                    print(weightQ[i], weightA[i], art)
                    # it's zero when there's no answers that passed the specialist IAA
                    # -1 is default answer value, it'll pass the ptsrec to the final score
                    if bestSourceTask!=0:
                        sourceData = sorcDic[bestSourceTask]
                        sourceUnits, sourceAns = sourceData[1], sourceData[0]
                    else:
                        sourceUnits = 0
                        sourceAns = -1
                    if bestArgTask!=0:
                        argData = argDic[bestArgTask]
                        argUnits, argAns = argData[1], argData[0]
                    else:
                        argUnits = []
                        argAns = -1
                    journalist = 'Joe The Journalist'
                    pts = assignPoints(ptsRec,wu, sourceUnits, argUnits, argAns, sourceAns, art, journalist)


                    print(schema)
                    #credId = counter
                    credId = schema[0]+str(counter)
                    counter+=1
                    starts, ends = indicesToStartEnd(wu)
                    addendum = [art, credId, schema, labels[i], pts, wu, starts[0], ends[0]]
                    outData.append(addendum)
                    #TODO: figure out how visualization handles stuff with multiple starts and ends
                    for i in range(len(starts)-1):
                        print('addendum', addendum)
                        print(labels)
                        print(len(ends), len(starts))
                        addendum = [art, credId, schema, labels[i+1], 0, wu, starts[i+1], ends[i+1]]
                        outData.append(addendum)
                print('exporting to csv')
                scores = open(directory + '/SortedPts_'+str(artNum)+'.csv', 'w', encoding='utf-8')
                print(directory + '/SortedPts_Master.csv')
                with scores:
                   writer = csv.writer(scores)
                   writer.writerows(outData)

    print("Table complete")
    print('Sources')
    print(sourceDatabase)
    print('Journalists')
    print(JournalistDatabase)
    print('Article Scores')
    print(ArticleDatabase)
def mergeWeightFiles(weightSet):
    df = pd.read_csv(weightSet[0])
    for i in range(1, len(weightSet)):
        weights = pd.read_csv(weightSet[i])
        df.append(weights, ignore_index = True)
    df.to_csv('combined_weights.csv')

def storeData(sourceFile, argRelFile, weightFile, allTuas):
    print(argRelFile)
    sourceData = pd.read_csv(sourceFile)
    argData = pd.read_csv(argRelFile)
    weightData = pd.read_csv(weightFile)
    tuas = pd.read_csv(allTuas)
    #by articles not by tasks
    #TODO: change this to article_sha256 after it works
    #Use article not tasks, finding which task best fits the weighting recommenation
    uqArticles = np.unique(argData['article_sha256'])
    bigDict = {}
    for art in uqArticles:
        artArgData = argData[argData['article_sha256'].notnull()]
        artArgData = artArgData[artArgData['article_sha256'] == art]
        artNum = artArgData['article_num'].iloc[0]
        taskAnsArg = getAnswersTask(artArgData)
        artSourceData = sourceData[sourceData['article_sha256'].notnull()]
        artSourceData = artSourceData[artSourceData['article_sha256'] == art]
        #there's many questions, only q 4 is relevant
        artQSourceData = artSourceData[artSourceData['question_Number'] == 4]
        taskAnsSource = getAnswersTask(artQSourceData)
        print(weightData.head(0))
        print(weightData['article_sha256'])
        print('betterartthanfart',art, type(art))
        printType(weightData['article_sha256'])
        artWeights = weightData[weightData['article_sha256'].notnull()]
        artWeights = artWeights[artWeights['article_sha256'] == art]
        weightTasks = artWeights['task_uuid'].tolist()
        labels = artWeights['Label'].tolist()
        weightInds = artWeights['highlighted_indices'].apply(get_indices_hard).tolist()
        print("WEIGHTINDS", weightInds)
        weightRec = artWeights['Points'].tolist()
        weightQs = artWeights['Question_Number'].tolist()
        weightAnswers = artWeights['Answer_Number'].tolist()
        weightDict = {}
        for t in range(len(weightTasks)):
            weightDict[weightTasks[t]] = {
                'indices':weightInds[t],
                'pointRec': weightRec[t],
                'label':labels[t],

            }
        #print('here')
        #print(artWeights['schema'])
        s = artWeights['schema']
        print('schemer',s)
        try:
            schema = s.iloc[0]
        except:
            schema = 'SCHEMANOTFOUND'
        argtasks = artArgData['task_uuid']
        taskTuaArg = {}
        for t in argtasks:
            #print('arg', t)
            tua = getTUA(t, tuas)
            #print(tua)
            taskTuaArg[t] = tua
        sorctasks = artQSourceData['task_uuid']
        print(sorctasks)
        taskTuaSourc = {}
        print('size',len(sorctasks))
        print(len(argtasks))
        for t in sorctasks:
            print('taskid',t)
            tua = getTUA(t, tuas)
            print(tua)
            taskTuaSourc[t] = tua
        argDict = mergeByTask(taskAnsArg, taskTuaArg)
        sorcDict = mergeByTask(taskAnsSource, taskTuaSourc)
        bigDict[art] = {
            'argDict':argDict,
            'sourceDict': sorcDict,
            'weightDict':weightDict,
            'labels':labels,
            'weightIndices': weightInds,
            'pointRec': weightRec,
            'weightQuestions':weightQs,
            'weightAnswers': weightAnswers,
            'schema': schema,
            'artNum': artNum
        }
    return bigDict
def runjson(targ):
    print(targ)
    return json.loads(targ)
def retrieveArtNum(data, article):
    return data[article]['artNum']
def retrieveweightDict(data, article):
    return data[article]['weightDict']
def retrieveArgDict(data, article):
    return data[article]['argDict']
def retrieveSourceDict(data, article):
    return data[article]['sourceDict']
def retrievesorctaskTua(data, article):
    return data[article]['sorctua']
def retrieveargtaskTua(data, article):
    return data[article]['argtua']
def getTUA(task, tuaDF):
    taskDF = tuaDF[tuaDF['quiz_task_uuid'] == task]
    tuas = []
    starts = []
    ends = []
    for t in taskDF['offsets']:
        formatted = json.loads(t)
        #print('formed', formatted)
        for f in formatted:
            starts.append(f[0])
            ends.append(f[1])
    indices = []
    for i in range(len(starts)):
        for n in range(starts[i], ends[i]):
            indices.append(n)
        #tuas.append((getStartsEndsFromString(t)))
    #print("TUAS", indices)
    #print('-------------------')
    return indices
def getStartsEndsFromString(bigStr):

    onStart = True
    starts = []
    ends = []
    ind = 0
    num = 0
    #TODO:if there's a number within the string this will freak out
    while ind<len(bigStr):
        if bigStr[ind].isdigit():
            if num>0:
                num = 10*num+int(bigStr[ind])
            else:
                num = int(bigStr[ind])
        else:
            if num!=0:
                if onStart:
                    starts.append(num)
                else:
                    ends.append(num)
                onStart = not onStart
                num = 0
        ind += 1
    indices = []
    for i in range(len(ends)):
        for n in range(starts[i], ends[i]):
            indices.append(n)
    print(indices)
    return np.unique(indices).tolist()

def indicesToStartEnd(indices):
    starts = []
    ends = []
    last = -1
    arr = np.array(indices)
    if len(indices)<1:
        return [-1],[-1]
    for i in range(len(indices)):
        if indices[i]-last>1 and indices[i] not in starts:
            starts.append(indices[i])
            ends.append(indices[i-1])
        last = indices[i]
    #ends.append(indices[len(indices)-1])
    print('starrt',starts, ends)
    return sorted(starts), sorted(ends)


def getSchema(data, article):
    return data[article]['schema']
def getTaskid(data, article):
    return data[article]['task']
def getweightQA(data, article):
    return data[article]['weightQuestions'], data[article]['weightAnswers']
def getpointRec(data, article):
    return data[article]['pointRec']
def getweightIndices(data,article):
    indices = data[article]['weightIndices']
    return indices



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


def getAnswersTask(artData):
    #indices = np.array(artData['highlighted_indices'].tolist())
    answers = np.array(artData['agreed_Answer'].tolist())
    tasks = np.array(artData['task_uuid'].tolist())
    passingVals = findNumVals(answers)
    #indices = indices[passingVals]
    answers = answers[passingVals]
    tasks = tasks[passingVals]
    #indices = [strLstToIntLst(ind) for ind in indices]
    d = {}
    for t in range(len(tasks)):
        d[tasks[t]] = answers[t]
    return d

def mergeByTask(answerDict, tuaDict):
    for k in answerDict.keys():
        if k in tuaDict.keys():
            temp = answerDict[k]
            answerDict[k] = (temp, tuaDict[k])
        else:
            temp = answerDict[k]
            answerDict[k] = (temp, [])
    return answerDict
def getFiles(directory):
    #NEEDS: WeightingOutputs, sourceTriagerIAA, arg Source IAA
    sourceFile = None
    argRelevanceFile = None
    weightOutputs = []
    for root, dir, files in os.walk(directory):
        for file in files:
            #print(file)
            if 'Dep_S_IAA' in file:
                print('siaa file-------------', file)
                if file.endswith('.csv')  and 'Quo' in file:
                    print("found Sources File" + directory + '/' + file)
                    sourceFile = directory+'/'+file
                if file.endswith('.csv')   and 'Arg' in file:
                    print('Found Arguments File '+ directory+'/' + file)
                    argRelevanceFile = directory+'/'+file
            if file.endswith('.csv')  and 'Point' in file:
                print('Found Weights File '+ directory+'/' + file)
                weightOutputs.append(directory+'/'+file)
    return sourceFile, argRelevanceFile, weightOutputs


def findNumVals(lst):
    indices = []
    for i in range(len(lst)):
        if lst[i].isdigit():
            indices.append(i)

    return indices


def findBestMatch(ptsUnits, modDict):
    """
    :param ptsUnits: one list of passing units
    :param modUnits: list of lists of units of the modifier
    :return: index of the best modifier Unit
    """
    bestTask =0
    bestScore = -1
    print("FINDING MATCH")
    for i in modDict.keys():
        print('key', i)
        modUnits = modDict[i][1]
        score, units = calcOverlap(modUnits, ptsUnits)
        if score>bestScore:
            bestScore = score
            bestTask = i
    print('winner', bestTask)
    return bestTask


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
    print(ptsRecUnitization, sourceUnitization)
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
    return ptsRec*argMult


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
    print('val', value)
    print('keeee', dict.keys())
    return dict[int(value)]


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
    print('checkedoneself')
    return doesPass, passingIndices


def calcOverlap(arr1, arr2):
    if isinstance(arr1, int) or isinstance(arr2, int) or len(arr1)<1 or len(arr2)<1:
        return 0,[]

    arr1 = get_indices_hard(str(arr1))
    arr2 = get_indices_hard((str(arr2)))
    print('arr1', arr1)
    print('arr2', arr2)
    arr1 = checkOneString(arr1)
    arr2 = checkOneString(arr2)
    print(type(arr1), type(arr2))
    #print(type(arr1[0]), type(arr2[0]))
    length = max(max(arr1), (max(arr2))) + 1

    answerMatrix = indicesToMatrix(arr1, arr2, length)
    percentageArray = np.array(scorePercentageUnitizing(answerMatrix, length, 2))
    passingIndices = np.nonzero(percentageArray == 1)[0]
    numPasses = len(passingIndices)
    rawScore = max((numPasses / len(arr1), numPasses / len(arr2)))
    return rawScore, passingIndices
def checkOneString(arr):
    if len(arr) == 1:
        if isinstance(arr[0], str):
            return get_indices_hard(arr)
    return arr


def indicesToMatrix(arr1, arr2, length):
    """converts lists of the indices of unitizations to an answer matrix"""
    print('arrimapirate',arr2)
    arr2 = [int(a) for a in arr2]
    arr1 = [int(a) for a in arr1]
    col1 = np.zeros(length)
    col2 = np.zeros(length)
    col1[arr1] = 1
    col2[arr2] = 1
    together = col1+col2
    unTogether = 2-together
    matrix = np.stack((together, unTogether),axis = 0).T
    return matrix


log = []
def sendPoints(target, points, targetDatabase):
    log.append(points)
    if target in targetDatabase.keys():
        targetDatabase[target] = targetDatabase[target]+points
    else:
        targetDatabase[target] = points


def getSource(sourceUnitizaiton):
    return 0

# print(checkAgreement([1,2,3,4], [1,2,3,4]))
#
# u1 = [3,4,5,6,7,8,9,10]
# u2 = [6,7,8,9,10,11,12,13]
# u3 = [1,2,3,4,5,6]
# u4 = [17,18,19,20,21]
#
# assignPoints(10,u1,u1,u1,3, 3, 1, 'bill')
# # print('source', sourceDatabase)
# # print('journalists', JournalistDatabase)
# # print('articles', ArticleDatabase)
# # assignPoints(10,u1,u1,u4,3,3,2, 'bill')
# # print('source', sourceDatabase)
# # print('journalists', JournalistDatabase)
# # print('articles', ArticleDatabase)
# # assignPoints(10,u1,u4,u4,3,3,2, 'bill')
# # print('source', sourceDatabase)
# # print('journalists', JournalistDatabase)
# # print('articles', ArticleDatabase)
# # assignPoints(10,u4,u4,u4,5,5,2, 'bill')
# # print('source', sourceDatabase)
# # print('journalists', JournalistDatabase)
# # print('articles', ArticleDatabase)
# #source,args,weight = getFiles('./demo1')
# #data = (storeData(source,args,weight))
# #print(data)
#pointSort('./pred1')
# print(sourceDatabase)
# print(ArticleDatabase)
# print(JournalistDatabase)
# print(log)
