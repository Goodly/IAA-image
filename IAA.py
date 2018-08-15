import csv

from ChecklistCoding import *
from ExtraInfo import *
from repScores import *

path = 'data_pull_8_10/PreAlphaSources-2018-08-10T0420-DataHuntHighlights.csv'


def calc_scores(filename, hardCodedTypes = False, repCSV=None):
    uberDict = data_storer(filename)
    data = [["article_num", "article_sha256", "question_Number", "agreed_Answer", "coding_Score", "highlighted_indices", \
             "alpha_unitizing_score", "alpha_unitizing_score_inclusive", "agreement_score", "num_users", "target_text",
             'question_text', 'answer_content']]
    if repCSV != None:
        repDF = CSV_to_userid(repCSV)
    else:
        repDF = create_user_dataframe(uberDict)
    for article in uberDict.keys():  # Iterates throuh each article
        article_num = get_article_num(uberDict, article)

        for ques in uberDict[article].keys():  # Iterates through each question in an article
            # print(repDF)

            agreements = score(article, ques, uberDict, repDF, hardCodedTypes = hardCodedTypes)
            # if it's a list then it was a checklist question
            question_text = get_question_text(uberDict, article, ques)
            if type(agreements) is list:
                for i in range(len(agreements)):
                    codingScore, unitizingScore = agreements[i][4], agreements[i][2]
                    totalScore = calcAgreement(codingScore, unitizingScore)
                    answer_text = get_answer_content(uberDict,article, ques, agreements[i][0])
                    data.append([article_num, article, ques, agreements[i][0], codingScore, agreements[i][1],
                                 unitizingScore, agreements[i][3], totalScore, agreements[i][5], agreements[i][6],
                                question_text, answer_text])
            else:
                codingScore, unitizingScore = agreements[4], agreements[2]
                #winner, units, uScore, iScore, highScore, numUsers
                answer_text = get_answer_content(uberDict, article, ques, agreements[0])
                totalScore = calcAgreement(codingScore, unitizingScore)
                data.append([article_num, article, ques, agreements[0], codingScore, agreements[1], unitizingScore, agreements[3],
                             totalScore, agreements[5], agreements[6], question_text, answer_text])

    # push out of womb, into world
    print('exporting rep_scores')
    # print(repDF)
    repDF.to_csv('RepScores/Repscore10.csv', mode='a', header=False)
    userid_to_CSV(repDF)
    print('exporting to csv')
    path, name = get_path(filename)
    scores = open(path+'S_IAA_'+name, 'w', encoding = 'utf-8')

    with scores:
        writer = csv.writer(scores)
        writer.writerows(data)

    print("Table complete")


def score(article, ques, data, repDF, hardCodedTypes = False):
    """calculates the relevant scores for the article
    returns a tuple (question answer most chosen, units passing the threshold,
        the Unitizing Score of the users who highlighted something that passed threshold, the unitizing score
        among all users who coded the question the same way (referred to as the inclusive unitizing score),
         the percentage agreement of the category with the highest percentage agreement """

    """ Commnted code below previously denoted different types of questions for hard-coding,
    can still be used for hard-coding but eventually will be phased out by a line of code that
    checks the type based off the table data"""
    # ordinal_questions = [1,2,4,12,13,14,15,16,17,18,19,20,21,25]
    # nominal_questions = [7,22]
    # unit_questions = [9,10,11, 24] #asks users to highlight, nothing else OR they highlight w/ txt answer
    # multiple_questions = [3,5,8,23]

    print('Scoring article: ', article, ' question: ', ques)

    starts, ends, length = get_question_start(data, article, ques).tolist(), get_question_end(data, article,
                                                                                              ques).tolist(), \
                           get_text_length(data, article, ques)
    texts = get_answer_texts(data, article, ques)
    sourceText = makeList(length)

    sourceText = addToSourceText(starts, ends, texts, sourceText)
    # TODO: find actual number of choices always
    num_choices = 5
    type = get_question_type(data, article, ques)
    if hardCodedTypes:
        type, num_choices = get_type_hard(type, ques)
    #This block for scoring only a single article, iuseful for debugging
    # print()
    # if article!= '171SSSArticle.txt':
    #     #print(type)
    #     if type == 'checklist':
    #         return [
    #             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #             [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    #
    #         ]
    #     return(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    if type == 'interval':
        # TODO: verify if these still exist, if they do, bring up to speed with new output formats
        return run_2step_unitization(data, article, ques, repDF)

    answers, users, numUsers = get_question_answers(data, article, ques).tolist(), \
                               get_question_userid(data, article, ques).tolist(), \
                               get_num_users(data, article, ques)
    if type == 'ordinal':
        out = evaluateCoding(answers, users, starts, ends, numUsers, length, repDF, sourceText, dfunc='ordinal')
        #print("ORDINAL", out[1], starts, ends)
        #do_rep_calculation_ordinal(users, answers, out[0], num_choices, out[1], starts, ends, length, repDF)
        return out
    elif type == 'nominal':
        out = evaluateCoding(answers, users, starts, ends, numUsers, length, repDF, sourceText)
        do_rep_calculation_nominal(users, answers, out[0], out[1], starts, ends, length, repDF)
        #print("NOMINAL", out[1], starts, ends)
        return out
    elif type == 'checklist':
        return evaluateChecklist(answers, users, starts, ends, numUsers, length, repDF, sourceText, num_choices = num_choices)


def calcAgreement(codingScore, unitizingScore):
    """averages coding and unitizing agreement scores to create a final agreement score to be used elsewhere in the
    Public Editor algorithm"""
    if codingScore == 'NA':
        return unitizingScore
    elif codingScore == 'L' or codingScore == 'M' or codingScore == 'U':
        return codingScore
    elif unitizingScore == 'NA':
        return codingScore
    elif unitizingScore == 'L' or unitizingScore == 'M' or unitizingScore == 'U':
        unitizingScore = 0

    return (float(codingScore) + float(unitizingScore)) / 2


def run_2step_unitization(data, article, question, repDF):
    starts, ends, length, numUsers, users = get_question_start(data, article, question).tolist(), get_question_end(data,
                                                                                                                   article,
                                                                                                                   question).tolist(), \
                                            get_text_length(data, article, question), get_num_users(data, article,
                                                                                                    question), get_question_userid(
        data, article, question).tolist()
    uqU = np.unique(users)
    userWeightDict = {}
    for u in uqU:
        userWeightDict[u] = get_user_rep(u, repDF)
    score, indices, iScore = scoreNuUnitizing(starts, ends, length, numUsers, users, userWeightDict)

    return 'NA', indices, score, score, 'NA'
#for purpose of naming outputFile
def get_path(fileName):
    name = ''
    path = ''
    for c in fileName:
        name = name +c
        if c == '/':
            path = path + name
            name = ''
    return path, name

# TEST STUFF
calc_scores('data_pull_8_10/PreAlphaLanguage-2018-08-10T0420-DataHuntHighlights.csv', hardCodedTypes=True)
#calc_scores(path, hardCodedTypes=True)
#in sss file I renamed the filenamecolumn to be sha256 so it fits in with the other mechanisms for extracting data
#calc_scores('data_pull_8_10/SSSPECaus2-2018-08-08T0444-DataHuntHighlights.csv', hardCodedTypes=True)