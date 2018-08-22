from CodingScoring import *
from repScores import *

def scoreChecklist(answers,numUsers, num_choices):
    out = []
    length = num_choices+1
    #index 1 refers to answer 1, 0 and the last item are not answerable
    scores = np.zeros(length)
    for a in answers:
        scores[a] = scores[a]+1
    for i in range(len(scores)):
        out.append(scores[i]/numUsers)
    return out

def evaluateChecklist(answers, users, starts, ends, numUsers, length, repDF,last30, sourceText, num_choices  = 5,  dfunc = None):
    repScaledAnswers, repScaledUsers = repScaleAnsUsers(answers, users, repDF)
    assert len(starts) == len(users), 'starts, users mismatched'
    percArray = scoreChecklist(repScaledAnswers.astype(int), len(repScaledUsers), num_choices)
    out = []
    for i in range(1,len(percArray)):
        codingScore = percArray[i]
        #scaledNumUsers and weighted stuff needs to change for each answer choice
        weights = np.zeros(len(percArray))
        weights[i] = 1
        assert len(starts) == len(users), 'starts, users mismatched'
        weightScaledAnswers, weightScaledUsers, weightScaledStarts, \
        weightScaledEnds, \
        weightScaledNumUsers, \
        userWeightDict = weightScaleEverything(answers, weights, users,
                                               starts, ends, repDF)
        assert len(weightScaledStarts) == len(weightScaledUsers), 'starts, users mismatched'
        winner, units, uScore, iScore, selectedText = passToUnitizing(weightScaledAnswers,weightScaledUsers,weightScaledStarts,
                                                        weightScaledEnds,numUsers,length, codingScore, i,
                                                        weightScaledNumUsers, userWeightDict, sourceText)
        firstSecondDiff = 1 - codingScore
        out.append([winner,units,uScore,iScore, codingScore, numUsers, selectedText, firstSecondDiff, 'checklist', num_choices])
        do_rep_calculation_nominal(users, answers, out[0], units, starts, ends, length, repDF,last30, checkListScale=(1/num_choices))

    return out

