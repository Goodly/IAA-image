from CodingScoring import *


def scoreChecklist(answers,numUsers):
    out = []
    length = max(answers)+1
    #index 1 refers to answer 1, 0 and the last item are not answerable
    scores = np.zeros(length)
    for a in answers:
        scores[a] = scores[a]+1
    for i in range(len(scores)):
        out.append(scores[i]/numUsers)
    return out

def evaluateChecklist(answers, users, starts, ends, numUsers, length, dfunc = None):
    repScaledAnswers, repScaledUsers = repScaleAnsUsers(answers, users)
    percArray = scoreChecklist(repScaledAnswers.astype(int), len(repScaledUsers.astype(int)))
    out = []
    for i in range(1,len(percArray)):
        codingScore = percArray[i]
        #scaledNumUsers and weighted stuff needs to change for each answer choice
        weights = np.zeros(len(percArray))
        weights[i] = 1
        weightScaledAnswers, weightScaledUsers, weightScaledStarts, \
        weightScaledEnds, \
        weightScaledNumUsers, \
        userWeightDict = weightScaleEverything(answers, weights, users,
                                               starts, ends)
        winner, units, uScore, iScore = passToUnitizing(weightScaledAnswers,weightScaledUsers,weightScaledStarts,
                                                        weightScaledEnds,numUsers,length, codingScore, i,
                                                        weightScaledNumUsers, userWeightDict)
        out.append([winner,units,uScore,iScore, codingScore])
    return out

