import pandas as pd
#add more input args if they are necessary for future use cases
def evaluateDependencies(schema, article, question, answer, dependenciesDF, stored,
                         indices, alphaAgreement, alphaInclusive, selectedText):
    depTo = checkDepended(schema, question, dependenciesDF, answer)
    if depTo:
        if depTo[depTo['dependency_type'] == 'unitizing']:
            dataTo = [indices, alphaAgreement, alphaInclusive, selectedText]
            stored = stashDepended(schema, article, question, answer, dataTo, stored)
        else:
            print('dependency type not recognized')
    depFrom = checkDependent(schema, question, dependenciesDF, answer)
    if depFrom:
        if depFrom[depFrom['dependency_type'] == 'unitizing']:
            dataTransfer = fetchDependent(schema,article, question, answer, stored)
            indices, alphaAgreement, alphaInclusive, selectedText = unPackDependent(dataTransfer)
        else:
            print('dependency type not recognized')
    return stored, indices, alphaAgreement, alphaInclusive, selectedText

def stashDepended(schema, article, question, answer, dataPassing, stored):
    if stored is None:
        stored = pd.DataFrame([schema, article, question, answer, dataPassing],
                              columns=['schema','article', 'question', 'answer', 'data'])
        return stored
    extension = pd.DataFrame([schema, article, question, answer, dataPassing],
                              columns=['schema','article', 'question', 'answer', 'data'])
    return stored.append(extension)

def unPackDependent(dataSeries):
    outs = []
    for i in range(len(dataSeries)):
        outs.append(dataSeries.iloc[0][i])
    return tuple(outs)

def fetchDependent(schema, article, question, answer, stored):
    try:
        schema = stored[stored['schema']==schema]
        art = schema[schema['article']==article]
        questionDf = art[art['question']==question]
        answerDf = questionDf[questionDf['answer']==answer]
    except KeyError:
        print("Not FOUND")
        return False
    return answerDf['data']

def getDependencies(path):
    dependenciesDF = pd.read_csv(path)
    return dependenciesDF

def checkDependent(schema, question, dependenciesDF, answer = -1):
    """checks if this question needs data passed into it from another question
    answer defaults to -1 because this is code for when all answers require
    external data
    returns false if no match, returns a filtered dataframe if it'll pass
    """
    return checkContained(schema, question, dependenciesDF, answer, 'question_to', 'answer_to')


def checkDepended(schema, question, dependenciesDF, answer = -1):
    """checks if this question needs data passed out of it from another question
    answer defaults to -1 because this is code for when all answers require
    external data
    returns false if no match, returns a filtered dataframe if it'll pass
    """
    return checkContained(schema, question, dependenciesDF, answer, 'question_from', 'answer_from')

def checkContained(schema, question, dependenciesDF, answer, quesHead, ansHead):
    thisSchema = dependenciesDF[dependenciesDF['schema'] == schema]
    print('thisschema',thisSchema)
    print('ques',question)
    if thisSchema.shape[0]<1:
        return False
    thisQ = thisSchema[thisSchema[quesHead] == question]
    if thisQ.shape[0] >0:
        print('passed shapeliness')
        if thisQ[ansHead].iloc[0] == -1:
            print('we in boooyyzzz')
            return thisQ
        match = thisQ[thisQ[ansHead] == answer]
        if match.shape[0] > 0:
            return match
        return False
    return False

