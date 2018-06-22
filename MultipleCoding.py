from KaOrdinalCoding import *

def scoreMultiple(answers,numUsers):
    out = []
    length = max(answers)+1
    #index 1 refers to answer 1, 0 and the last item are not answerable
    scores = np.zeros(length)
    for a in answers:
        scores[a] = scores[a]+1
    #print(scores)
    for i in range(len(scores)):
        out.append(scores[i]/numUsers)
    #print (winner)
    #print(topScore)
    return out

def evaluateMultiple(answers, users, starts, ends, numUsers, length, dfunc = None):
    percArray = scoreMultiple(answers, numUsers)
    out = []
    for i in range(1,len(percArray)):
        relevantUsers = getUsers(i, users, answers)
        score = percArray[i]
        unitizedScore = passToUnitizing(answers,users,starts,ends,numUsers,length, score, i, relevantUsers)
        out.append(unitizedScore)
    return out
ans1 = [1,3,4,1,2,3,4,1,2,3,5,6,3,1,2,1,3,4,2,1,2,2,2,1,1,3,3]
ans2 = [1,1,1,2,2,2,1,1,1]
ans3 = [1,1,1,1,1,4,4,4,4,4]
ans4 = [1,2,2,1,2,3]
users= [6,5,4,3,2,1]
