
import numpy as np
from jnius import autoclass

CAS = autoclass('org.dkpro.statistics.agreement.coding.CodingAnnotationStudy')
KAA = autoclass('org.dkpro.statistics.agreement.coding.KrippendorffAlphaAgreement')
NDF = autoclass('org.dkpro.statistics.agreement.distance.NominalDistanceFunction')
ODF = autoclass('org.dkpro.statistics.agreement.distance.OrdinalDistanceFunction')
Integer = autoclass('java.lang.Integer')



ordinal_questions = ['2','4','6','13','14','15','16','17','18','19','20','21','25']
nominal_questions = ['7','22']
interval_questions = ['9','10','11'] #asks users to highlight, nothing else
multiple_questions = ['3','5','8',]

def Score(article, ques):
    """Call this to get what you want
    It'll check for different types of questionsAnswered
    ifit's an interval question it'll return a random number """
    if ques in interval_questions:
        return np.Random.choice(1) #Unitize Score
    responses = get_responses(article,ques)
    if ques in ordinal_questions:
        return (pickWinnerBecauseAlgorithmsTeamWantsMeToUgh(responses)), scoreOrdinal(responses)
    elif ques in nominal_questions:
        return (pickWinnerBecauseAlgorithmsTeamWantsMeToUgh(responses)), scoreNominal(responses)
    elif ques in multiple_questions:
        return scoreMultiple(responses, get_user_count(article, ques))

def pickWinnerBecauseAlgorithmsTeamWantsMeToUgh(responses):
    """https://stackoverflow.com/questions/6252280/find-the-most-frequent-number-in-a-numpy-vector"""
    a = np.make_array(response)
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
    return "observed ", observed, "expected ", expected, "agreement ", agreement, "cat1", cat1, "Disage", observed/(len(responses)**2)*5.75

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

def genMult(responses):
    return ['1','2','3','1','1','2']
def genPerf(responses):
    return ['1','1','1','1']
def genWorst(responses):
    return ['1','2','3','4','5','6']
def genWorst(responses):
    return ['1','2','3','4','5','6']
