import pandas as pd
import numpy as np
from jnius import autoclass

CAS = autoclass('org.dkpro.statistics.agreement.coding.CodingAnnotationStudy')
KAA = autoclass('org.dkpro.statistics.agreement.coding.KrippendorffAlphaAgreement')
NDF = autoclass('org.dkpro.statistics.agreement.distance.NominalDistanceFunction')
ODF = autoclass('org.dkpro.statistics.agreement.distance.OrdinalDistanceFunction')
Integer = autoclass('java.lang.Integer')

def calc_scores(filename):
    data = pd.read_csv(filename)
    uberDict = csv_to_dict(data)
    #@TODO initialize csv file here, and any writer we would need
    for artic in uberDict.keys(): #Find a way to iterate through only articles that there agreement
        for ques in uberDict[artic].keys(): #get a way to iterate through questions in the csv
            agreements = score(artic, ques, uberDict)
            print(agreements)
            #@TODO add to the csv, one column of the 'correct' question answer is agreements[0], degree of agreement is agreements[1]
    #@TODO return the csv, or make sure it's pushed out of the womb and into the world

def get_responses(article, question, csv_dict):
    return csv_dict[article][question][1:]

def get_user_count(article,question, csv_dict):
    return csv_dict[article][question][0]

def csv_to_dict(csv):
    articles = np.unique(csv['taskrun_article_number'])
    return_dict = dict()
    for i in articles:
        return_dict[i] = dict()
        article_tbl = csv[csv['taskrun_article_number'] == i]
        questions = np.unique(article_tbl['question_number'])
        for n in questions:
            answers = article_tbl['answer_number']
            num_answers = len(answers)
            answer_arr = [num_answers] + answers
            return_dict[i][n] = answer_arr
    return return_dict

def score(article, ques, data):
    """Call this to get what you want
    It'll check for different types of questionsAnswered
    ifit's an interval question it'll return a random number

    returns a tuple, element 0 is winning answer, element 1 is the disagreement score """
    ordinal_questions = [1,2,4,5,13,14,15,16,17,18,19,20,21,25]
    nominal_questions = [7,22]
    interval_questions = [9,10,11] #asks users to highlight, nothing else
    multiple_questions = [3,5,8]
    if ques in interval_questions:
        return np.Random.choice(1) #Unitize Score
    responses = get_responses(article,ques,data)
    if ques in ordinal_questions:
        return (pickWinnerBecauseAlgorithmsTeamWantsMeToUgh(responses)), 1- scoreOrdinal(responses)
    elif ques in nominal_questions:
        return (pickWinnerBecauseAlgorithmsTeamWantsMeToUgh(responses)), 1- scoreNominal(responses)
    elif ques in multiple_questions:
        return scoreMultiple(responses, get_user_count(article, ques,data))

def pickWinnerBecauseAlgorithmsTeamWantsMeToUgh(responses):
    """https://stackoverflow.com/questions/6252280/find-the-most-frequent-number-in-a-numpy-vector"""
    a = np.array(responses)
    (values,counts) = np.unique(a,return_counts=True)
    ind=np.argmax(counts)
    return values[ind]

def toStudy(responses):
    intResponses = [Integer(int(i)) for i in responses]
    size = len(intResponses)
    study = CAS(size)
    study.addItemAsArray(intResponses)
    return study

def toAlpha(study, dFunc):
    alph = KAA(study,dFunc())
    return alph

def scoreNominal(responses):
    study = toStudy(responses)
    alpha = toAlpha(study, NDF)
    return alpha.calculateObservedDisagreement()

def scoreOrdinal(responses):
    study = toStudy(responses)
    alpha = toAlpha(study, ODF)
    observed = alpha.calculateObservedDisagreement()
    expected = alpha.calculateExpectedDisagreement()
    agreement = alpha.calculateAgreement()
    cat1 = alpha.calculateCategoryAgreement(Integer(1))
    val = (observed/(len(responses)**2)*5.75-.6)*2.5
    if val<0:
        return 0
    elif val >1:
        return 1
    return 1- val

def scoreInterval():
    return 0

def scoreMultiple(responses,numUsers):
    out = dict()
    for r in responses:
        scor = nomList(responses, r, numUsers)
        out[r] = scor
    return out

def nomList(responses, r, numUsers):
    base = np.zeros(len(responses))
    for i in np.arange(len(base)):
        if responses[i] == r:
            base[i] = 1
    return sum(base)/numUsers
