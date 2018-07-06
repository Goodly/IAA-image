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
    percArray = scoreChecklist(answers, numUsers)
    out = []
    for i in range(1,len(percArray)):
        codingScore = percArray[i]
        winner, units, uScore, iScore = passToUnitizing(answers,users,starts,ends,numUsers,length, codingScore, i)
        out.append([winner,units,uScore,iScore, codingScore])
    return out
