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
    weights = np.ones(max(answers)+1)
    weightScaledAnswers, weightScaledUsers, weightScaledStarts, \
                                            weightScaledEnds, \
                                            weightScaledNumUsers = weightScaleEverything(answers, weights, users,
                                                                                         starts,ends)
    percArray = scoreChecklist(weightScaledAnswers, weightScaledNumUsers)
    out = []
    for i in range(1,len(percArray)):
        codingScore = percArray[i]
        winner, units, uScore, iScore = passToUnitizing(weightScaledAnswers,weightScaledUsers,weightScaledStarts,
                                                        weightScaledEnds,numUsers,length, codingScore, i, weightScaledNumUsers)
        out.append([winner,units,uScore,iScore, codingScore])
    return out
