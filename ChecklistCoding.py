from CodingScoring import *
#from repScores import *

def scoreChecklist(answers,numUsers, num_choices):
    out = []
    print('answers', answers, num_choices)
    length = num_choices+1
    #index 1 refers to answer 1, 0 and the last item are not answerable
    answers = [int(a) for a in answers]
    scores = np.zeros(length)
    for a in answers:
        scores[a] = scores[a]+1
    for i in range(len(scores)):
        print('scores', scores, numUsers)
        out.append(scores[i]/numUsers)
    return out

def evaluateChecklist(answers, users, starts, ends, numUsers, length, repDF,sourceText, hlUsers, hlAns, num_choices  = 5,  dfunc = None):
    print("CHECKLIST NUM USERS", numUsers)

    repScaledAnswers, repScaledUsers = repScaleAnsUsers(answers, users, repDF)
    #assert len(starts) == len(users), 'starts, users mismatched'
    print('prepercNumUsers', numUsers)
    #TODO: scale numUsers when repScaled gets scaled up
    percArray = scoreChecklist(repScaledAnswers, numUsers, num_choices)
    out = []
    print('got percAray')
    for i in range(1,len(percArray)):
        codingScore = percArray[i]
        #scaledNumUsers and weighted stuff needs to change for each answer choice
        weights = np.zeros(len(percArray))
        weights[i] = 1
#        assert len(starts) == len(users), 'starts, users mismatched'
        assert(len(answers) == len(users))
        weightScaledAnswers, weightScaledUsers, weightScaledHlUsers, \
        weightScaledStarts, \
        weightScaledEnds, \
        weightScaledNumUsers, \
        userWeightDict = weightScaleEverything(hlAns, weights, users, hlUsers,
                                               starts, ends, repDF)
        # weightScaledAnswers, weightScaledUsers, weightScaledStarts, \
        # weightScaledEnds, \
        # weightScaledNumUsers,  = hlAns, hlUsers, starts, ends, numUsers
        # print('clnumusers', weightScaledUsers)
        #assert len(weightScaledStarts) == len(weightScaledUsers), 'starts, users mismatched'
        #TODO: weight scale the hlUsers
        print('passing to utizing')
        winner, units, uScore, iScore, selectedText = passToUnitizing(weightScaledAnswers,weightScaledHlUsers, users, weightScaledStarts,
                                                        weightScaledEnds,numUsers,length, codingScore, i,
                                                        weightScaledNumUsers, userWeightDict, sourceText)
        firstSecondDiff = 1 - codingScore
        out.append([winner,units,uScore,iScore, codingScore, numUsers, selectedText, firstSecondDiff, 'checklist', num_choices])
        #do_rep_calculation_nominal(users, answers, out[0], units, starts, ends, length, repDF,last30, checkListScale=(1/num_choices))

    return out

