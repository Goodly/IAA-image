import csv
from ChecklistCoding import *
from ExtraInfo import *
from repScores import *
from data_utils import initRep
from QuestionDependencies import getDependencies
from QuestionDependencies import evaluateDependencies
import os
path = 'sss_pull_8_22/SSSPECaus2-2018-08-22T2019-DataHuntHighlights.csv'

def calc_agreement_directory(directory, hardCodedTypes = False, repCSV=None, dependencyCSV = 'Inter_q_dependencies.csv', answersFile = None):
    for root, dir, files in os.walk(directory):
        for file in files:
            if file.endswith('.csv') and 'IAA' not in file:
                print("Checking Agreement for "+directory+'/'+file)
                try:
                    calc_scores(directory+'/'+file, hardCodedTypes=hardCodedTypes, repCSV = repCSV, dependencyCSV = dependencyCSV,
                            answersFile = answersFile)
                except:
                    #will be an error for every file that isn't the right file, there's a more graceful solution, but
                    #we'll save that dream for another day
                    print("ERROR OCCURRED")

def calc_scores(filename, hardCodedTypes = False, repCSV=None, dependencyCSV = 'Inter_q_dependencies.csv', answersFile = None):
    uberDict = data_storer(filename, answersFile)
    data = [["article_num", "article_sha256", "question_Number", "question_type", "agreed_Answer", "coding_perc_agreement", "one_two_diff",
             "highlighted_indices", "alpha_unitizing_score", "alpha_unitizing_score_inclusive", "agreement_score","odds_by_chance", "binary_odds_by_chance",
             "num_users", "num_answer_choices","target_text", 'question_text', 'answer_content']]
    #initialize rep
    repDF = initRep(repCSV, uberDict)
    #initialize inter-question dependencies
    storedForDepend = None
    dependenciesDF = getDependencies(dependencyCSV)
    for article in uberDict.keys():  # Iterates throuh each article
        article_num = get_article_num(uberDict, article)

        for ques in uberDict[article].keys():  # Iterates through each question in an article
            # print(repDF)

            agreements = score(article, ques, uberDict, repDF, hardCodedTypes = hardCodedTypes)
            # if it's a list then it was a checklist question
            question_text = get_question_text(uberDict, article, ques)
            if type(agreements) is list:
                #Checklist Question
                for i in range(len(agreements)):
                    codingPercentAgreement, unitizingScore = agreements[i][4], agreements[i][2]
                    winner, units = agreements[i][0], agreements[i][1]
                    inclusiveUnitizing = agreements[i][3]
                    selectedText, firstSecondScoreDiff = agreements[i][6], agreements[i][7]
                    question_type, num_choices = agreements[i][8], agreements[i][9]
                    num_users = agreements[i][5]
                    storedForDepend, units, unitizingScore, inclusiveUnitizing, selectedText = evaluateDependencies(question_type,
                                                                                                article, ques, winner,
                                                                                                dependenciesDF,
                                                                                                storedForDepend, units,
                                                                                                unitizingScore,
                                                                                                inclusiveUnitizing,
                                                                                                selectedText)
                    totalScore = calcAgreement(codingPercentAgreement, unitizingScore)
                    answer_text = get_answer_content(uberDict,article, ques, agreements[i][0])
                    bin_chance_odds = oddsDueToChance(codingPercentAgreement,num_users=num_users, num_choices=2)
                    #Treat each q as a binary yes/no
                    chance_odds = bin_chance_odds
                    ques_num = parse(ques,'Q')
                    data.append([article_num, article[:8], ques_num, agreements[i][8], agreements[i][0], codingPercentAgreement, agreements[i][7], agreements[i][1],
                                 unitizingScore, agreements[i][3], totalScore, chance_odds, bin_chance_odds, num_users, agreements[i][9],agreements[i][6],
                                question_text, answer_text])
            else:
                #winner, units, uScore, iScore, highScore, numUsers, selectedText, firstSecondScoreDiff
                winner, units = agreements[0], agreements[1]
                inclusiveUnitizing, numUsers = agreements[3], agreements[5]
                selectedText, firstSecondScoreDiff = agreements[6], agreements[7]
                question_type, num_choices = agreements[8], agreements[9]
                codingPercentAgreement, unitizingScore = agreements[4], agreements[2]

                num_users = agreements[5]
                storedForDepend, units, unitizingScore, inclusiveUnitizing, selectedText = evaluateDependencies(question_type,
                                                                                                  article, ques, winner,
                                                                                                  dependenciesDF,
                                                                                                  storedForDepend, units,
                                                                                                  unitizingScore,
                                                                                                  inclusiveUnitizing,
                                                                                                  selectedText)
                bin_chance_odds = oddsDueToChance(codingPercentAgreement,num_users=num_users, num_choices=2)
                chance_odds = oddsDueToChance(codingPercentAgreement,num_users=num_users, num_choices=num_choices)
                answer_text = get_answer_content(uberDict, article, ques, agreements[0])
                totalScore = calcAgreement(codingPercentAgreement, unitizingScore)
                ques_num = parse(ques, 'Q')
                data.append([article_num, article[:8], ques_num, agreements[8], winner, codingPercentAgreement, agreements[7],
                             units, unitizingScore, inclusiveUnitizing,
                             totalScore, chance_odds, bin_chance_odds, num_users, agreements[9], selectedText,
                             question_text, answer_text])

    # push out of womb, into world
    print('exporting rep_scores')
    # print(repDF)
#    repDF.to_csv('RepScores/Repscore10.csv', mode='a', header=False)
 #   userid_to_CSV(repDF)
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
    checks the question_type based off the table data"""
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
    question_type = get_question_type(data, article, ques)
    if hardCodedTypes:
        question_type, num_choices = get_type_hard(question_type, ques)
    #This block for scoring only a single article, iuseful for debugging
    # print()
    # if article!= '171SSSArticle.txt':
    #     #print(question_type)
    #     if question_type == 'checklist':
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
    if question_type == 'interval':
        # TODO: verify if these still exist, if they do, bring up to speed with new output formats
        return run_2step_unitization(data, article, ques, repDF)

    answers, users, numUsers = get_question_answers(data, article, ques), \
                               get_question_userid(data, article, ques).tolist(), \
                               get_num_users(data, article, ques)
    if question_type == 'ordinal':
        out = evaluateCoding(answers, users, starts, ends, numUsers, length, repDF, sourceText, dfunc='ordinal')
        #print("ORDINAL", out[1], starts, ends)
        #do_rep_calculation_ordinal(users, answers, out[0], num_choices, out[1], starts, ends, length, repDF)
        out = out+(question_type, num_choices)
    elif question_type == 'nominal':
        out = evaluateCoding(answers, users, starts, ends, numUsers, length, repDF, sourceText)
        #do_rep_calculation_nominal(users, answers, out[0], out[1], starts, ends, length, repDF)
        #print("NOMINAL", out[1], starts, ends)
        out = out+(question_type, num_choices)
    elif question_type == 'checklist':
        out = evaluateChecklist(answers, users, starts, ends, numUsers, length, repDF, sourceText, num_choices = num_choices)
    return out


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

# # TEST STUFF
#calc_agreement_directory('demo1',  hardCodedTypes=True)

#calc_scores('demo1/Demo1Prob-2018-08-28T2257-DataHuntHighlights.csv', hardCodedTypes= True)
# # calc_scores('data_pull_8_10/PreAlphaLanguage-2018-08-10T0420-DataHuntHighlights.csv', hardCodedTypes=True)
#calc_scores(path, hardCodedTypes=True)
# #in sss file I renamed the filenamecolumn to be sha256 so it fits in with the other mechanisms for extracting data
# calc_scores('data_pull_8_10/SSSPECaus2-2018-08-08T0444-DataHuntHighlights.csv', hardCodedTypes=True)
# calc_scores('data_pull_8_17/ArgumentRelevance1.0C2-2018-08-17T2012-DataHuntHighlights.csv')
# # calc_scores('data_pull_8_17/ArgumentRelevance1.0C2-2018-08-17T2012-DataHuntHighlights.csv')
# # calc_scores('data_pull_8_17/ArgumentRelevance1.0C2-2018-08-17T2012-DataHuntHighlights.csv')
