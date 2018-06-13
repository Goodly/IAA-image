import pandas as pd
import numpy as np
import csv
from jnius import JavaException as JE
from jnius import autoclass


CAS = autoclass('org.dkpro.statistics.agreement.coding.CodingAnnotationStudy')
UAS = autoclass('org.dkpro.statistics.agreement.unitizing.UnitizingAnnotationStudy')
UAU = autoclass('org.dkpro.statistics.agreement.unitizing.UnitizingAnnotationUnit')
KAUA = autoclass('org.dkpro.statistics.agreement.unitizing.KrippendorffAlphaUnitizingAgreement')
KAA = autoclass('org.dkpro.statistics.agreement.coding.KrippendorffAlphaAgreement')
NDF = autoclass('org.dkpro.statistics.agreement.distance.NominalDistanceFunction')
ODF = autoclass('org.dkpro.statistics.agreement.distance.OrdinalDistanceFunction')
Integer = autoclass('java.lang.Integer')
Iterable = autoclass('java.lang.Iterable')
Float = autoclass('java.lang.Float')

path = './pe_data/SSSPECaus2-2018-05-03T23.csv'

def calc_scores(filename):
        data = pd.read_csv(filename)
        uberDict = data_storer(data)
        #@TODO initialize csv file here, and any writer we would need
        data = [["Article Number", "Question Number", "Agreed Answer", "Coding Score", "Unitizing Score"]]

        for article in uberDict.keys(): #Find a way to iterate through only articles that there agreement
            for ques in uberDict[article].keys(): #get a way to iterate through questions in the csv
                print(article, ques)
                agreements = score(article, ques, uberDict)
                #print(agreements[1])
                #print(agreements)
                #@TODO add nnto the csv, one column of the 'correct' question answer is agreements[0], degree of agreement is agreements[1]
                if type(agreements) is dict:
                    for k in agreements.keys():
                        data.append([article,ques, k, agreements[k][0], agreements[k][1]])
                else:
                    data.append([article,ques, agreements[0], agreements[1], agreements[2]])
        #@TODO return the csv, or make sure it's pushed out of the womb and into the world

        scores = open('question_scores.csv', 'w')

        with scores:
            writer = csv.writer(scores)
            writer.writerows(data)

        print("Table complete")

def get_responses(article, question, csv_dict):
    return csv_dict[article][question][1:]

def get_user_count(article,question, csv_dict):
    return csv_dict[article][question][0]

def data_storer(data):
    article_nums = np.unique(data['taskrun_article_number'])
    dict_of_article_df = dict()
    for i in article_nums:
        article =data[data['taskrun_article_number'] == i]
        question_nums = np.unique(article['question_number'])
        new_dict = dict()
        for x in question_nums:
            array = []
            array.append(article.loc[article['question_number']== x, 'question_text'][0:1])
            answers = [article.loc[article['question_number']== x, 'answer_number']]
            answers.append([article.loc[article['question_number']== x, 'contributor_id']])
            answers.append([article.loc[article['question_number']== x, 'start_pos']])
            answers.append([article.loc[article['question_number']== x, 'end_pos']])
            answers.append([article.loc[article['question_number']== x, 'source_text_length']])
            array.append(answers)

            new_dict[x] = array
            #this is where krippendorf goes
        dict_of_article_df[i] = new_dict
    return dict_of_article_df

def get_question_answers(data, article_num, question_num):
    return data[article_num][question_num][1][0]

def get_question_userid(data, article_num, question_num):
    return data[article_num][question_num][1][1]

def get_question_start(data, article_num, question_num):
    return data[article_num][question_num][1][2]

def get_question_end(data, article_num, question_num):
    return data[article_num][question_num][1][3]

def get_text_length(data, article_num, question_num):
    return data[article_num][question_num][1][4]
    #Old Categories
    # ordinal_questions = [1,2,4,5,12,13,14,15,16,17,18,19,20,21,25]
    # nominal_questions = [7,22]
    # interval_questions = [9,10,11, 24] #asks users to highlight, nothing else OR they highlight w/ txt answer
    # multiple_questions = [3,5,8,23]

def score(article, ques, data):
    """Call this to get what you want
    It'll check for different types of questionsAnswered
    ifit's an interval question it'll return a random number

    returns a tuple, element 0 is winning answer, element 1 is the disagreement score """
    ordinal_questions = [1, 8, 9, 12, 13]
    nominal_questions = [5, 10]
    interval_questions = [7, 11]
    multiple_questions = [6]
    print('article ', article, ' question ', ques)
    Users = get_question_userid(data,article, ques)[0]
    print(Users)
    numUsers = len(np.unique(Users))
    uStudy = CAS(numUsers)
    if ques in interval_questions:

        return ("n/a", "n/a", unitize(data,article,ques,[])) #Unitize Score
        #n/a corresponds to the situation in which there is no agreed upon answer
    responses = get_question_answers(data, article, ques)
    if ques in ordinal_questions:
        winner = pickWinnerBecauseAlgorithmsTeamWantsMeToUgh(responses)
        return winner, 1- scoreOrdinal(responses), unitize(data,article,ques, responses, winner=winner)
    elif ques in nominal_questions:
        winner = pickWinnerBecauseAlgorithmsTeamWantsMeToUgh(responses)
        return winner, 1- scoreNominal(responses), unitize(data,article,ques, responses, winner=winner)
    elif ques in multiple_questions:
        return scoreMultiple(responses, Users, data, article, ques)

def pickWinnerBecauseAlgorithmsTeamWantsMeToUgh(responses):
    """https://stackoverflow.com/questions/6252280/find-the-most-frequent-number-in-a-numpy-vector"""
    a = np.array(responses)
    (values,counts) = np.unique(a,return_counts=True)
    ind=np.argmax(counts)
    return values[ind]



def unitize(data,article,ques, responses, winner = 0):
    starts, ends, ids, length = get_question_start(data,article,ques)[0].tolist(), \
        get_question_end(data,article,ques)[0].tolist(), get_question_userid(data,article,ques)[0].tolist(), \
        max(get_text_length(data,article,ques)).max()
    if length == 0:
        return 'n/a'
    # if winner is not None:
    #     liveIndices = []
    #     for a in range(len(starts)):
    #         if responses.iloc[a] == winner:
    #             liveIndices.append(a)
    #         tempstarts,tempends,tempids,templen = [],[],[],[]
    #         for index in liveIndices:
    #             tempstarts.append(starts[index])
    #             tempends.append(ends[index])
    #             tempids.append(ids[index])
    #     starts = tempstarts
    #     ends = tempends
    #     ids = tempids
    # deadIndices = []
    # for i in range(len(ends)):
    #     if ends[i] == 0:
    #         deadIndices.append(i)
    # for i in range(len(deadIndices)):
    #     index = len(deadIndices)-1
    #     starts.pop(index)
    #     ends.pop(index)
    #     ids.pop(index)
    #     deadIndices.pop()
    if len(starts)<=0:
        return 'n/a'
    return scoreUnitizing(starts,ends,ids,length,responses, winner)

def toPrimInt(i):
    try:
        return int(i)
    except ValueError:
        return - 1
def toUnitizingStudy(begins, ends, ids, arLength, answers):
    intBegins = [(int(i)) for i in begins]
    intEnds = [(int(i)) for i in ends]
    intIDs = [toPrimInt(i) for i in ids]
    size = len(intBegins)
    if len(intBegins) != len(intEnds):
        print("begins and ends not the same")
        return None
    units = []
    numRaters = (len(np.unique(ids)))
    uStudy = UAS(numRaters, min(intBegins), max(intEnds))
    for i in range(size):
        offset = intBegins[i]
        length = intEnds[i]-intBegins[i]
        uID = intIDs[i]

        category = (str(answers.iloc[i]))#category might matter, if it does let's stop using 1
        #print(category, category.intValue())
        units.append([float(offset),float(length),uID,category])
        uStudy.addUnit((offset),(length),uID,category)
    print(units)
    return uStudy, units

def scoreUnitizing(begins, ends, ids, arLength,responses, winner = 0):
    study, units = toUnitizingStudy(begins, ends, ids, arLength, responses)
    ##test-suite necessary code below:
    #printUnitizingStudy(study)
    ##END TEST-suite stuuff
    alpha = KAUA(study)
    count = 0
    for u in units:
        if u[3] == str(winner):
            count+=1
    print(count, 'units of winning category')
    if (arLength == 0 or len(begins) <2):
        #print("division by zero,returning na", len(begins))
        return 'Only1Ans'
    try:
        print("winner:", winner)
        print(alpha.calculateCategoryAgreement(str(winner)))
        return alpha.calculateCategoryAgreement(str(winner))
    except JE:
        print("Divided by 0")
        return ("N?A")

def toStudy(responses):
    #print(responses)
    intResponses = [Integer(int(i)) for i in responses]
    #print("Integer Objects:")
    #print([i.intValue() for i in intResponses])
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
    val = (1-(observed/(len(responses)**2)*5.75-.6))/1.6
    # if val<0:
    #     return 0
    # elif val >1:
    #     return 1
    return val


#split into different questions, and IAA each one as if it was a yes/no for each option
def scoreMultiple(responses,Users, data, article, ques):
    out = dict()
    numUsers = len(np.unique(Users))
    uqResponses = np.unique(responses)
    for r in uqResponses:
        scor = nomList(responses, r, numUsers, Users)
        unit = unitize(data, article, ques, responses, winner = r)
        out[r] = scor,unit
    return out


def nomList(responses, r, numUsers, users):
    l = len(responses)
    binaryAnswers = np.zeros(numUsers)
    tot = 0
    i = 0
    uCounted = []
    uqUsers = np.unique(users)
    for resp in responses:
        if (i>=len(uqUsers)):
            break
        else:
            user= uqUsers[i]
            if resp == r:
                if user not in uCounted:
                #uCounted.append(users.iloc[i])
            #tot+=1
                    uCounted.append(user)
                    binaryAnswers[i] = 1
                    i+=1

        #i+=1
    return scoreNominal(binaryAnswers.tolist())
    #return tot/numUsers




    #----------Test Suites below----------------
    # def unitizingTest():
    #     study = toUnitizingStudy([39,18,45,60,140], [60,40,70,65,180], [1,2,3,2,1],230)
    #     return KAUA(study)
    #
    # def unitizingSame():
    #     return KAUA(toUnitizingStudy([39,39,39,39,39], [60,60,60,60,60], [1,2,3,4,5],230))
    #
    # def unitizingDiff():
    #     return KAUA(toUnitizingStudy([0,10,20,30,40], [10,20,30,40,50], [1,2,3,4,5],50))
    #
def printUnitizingStudy(study):
    us = study.getUnits().iterator()
    while us.hasNext():
        u = us.next()
        print("UNIT: O:", u.getOffset(),"L:",u.getLength())


    def manyTests(numTests):
        answers = np.zeros(numTests)
        for i in range(numTests):
            stud = unitizingRandom()
            alpha = KAUA(stud)
            ans = alpha.calculateCategoryAgreement(Integer(1))
            #category is 1 because the unitizingstudy decides category of everything is 1
            answers[i] = ans
        return answers

        def unitizingRandom():
            length = np.random.randint(20)+5
            size = np.random.randint(1000)+100
            begs,  users = randArray(length, minRange = size),  randArray(length, minRange = 10)
            ends = randAddtoArray(50, begs)
            #print(begs,ends,users,size)
            return (toUnitizingStudy(begs,ends,users,size))

def manyTestsNew(numTests):
    answers = np.zeros(numTests)
    for i in range(numTests):
        length = np.random.randint(20)+5
        size = np.random.randint(1000)+100
        begs,  users = randArray(length, minRange = size),  randArray(length, minRange = 10)
        ends = randAddtoArray(50, begs)
        ans = scoreUnitizing(begs, ends,users, length)
        answers[i] = ans
    return answers
    #
    # def getScoreBreakdown(lst):
    #     plt.hist(lst)
    #
def randArray(length, minRange = 100):
    return np.random.randint(minRange, size = length)

def randAddtoArray(maxAddition, oldArray):
    newArray = np.zeros(len(oldArray))
    for i in range(len(oldArray)):
        add = np.random.randint(maxAddition)
        newArray[i] = oldArray[i]+maxAddition
    return newArray
