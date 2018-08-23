import pandas as pd
import numpy as np
from repScores import *

def fetch_for_triage(path):
    js = pd.read_json(path)
    articles = js['article_number'].tolist()
    bigDict = {}
    for i in range(len(articles)):
        art = articles[i]
        htasks = js['highlight_tasks']
        for t in range(len(htasks[i])):
            htask = htasks[i][t]
            hruns = htask['highlight_taskruns']
            flags = []
            starts, ends = [], []
            cats,users = [], []
            for run in hruns:
                include_in_IAA = run['include_in_IAA']
                if include_in_IAA:
                    highlights = run['highlights']
                    for highlight in highlights:
                        flags.append(highlight['case_number'])
                        starts.append(highlight['offsets'][0][0])
                        ends.append(highlight['offsets'][0][1])
                        cats.append(highlight['topic_name'])
                        users.append(run['contributor']['unique_label'])
        bigDict[art] = {'starts':starts,
                        'ends': ends,
                        'users': users,
                        'flags': flags,
                        'cats': cats
                    }
    return bigDict, articles

def data_storer(path, answerspath):
    """Function that turns csv data. Input the path name for the csv file.
    This will return a super dictionary that is used with other abstraction functions."""

    highlightData = pd.read_csv(path, encoding = 'utf-8')
    if answerspath is not None:
        answersData = pd.read_csv(answerspath, encoding = 'utf-8')
    article_nums = np.unique(highlightData['article_sha256'])
    dict_of_article_df = dict()
    for i in article_nums:
        article =highlightData[highlightData['article_sha256'] == i]
        question_nums = np.unique(article['question_label'])
        new_dict = dict()
        for x in question_nums:
            array = []
            array.append(article.loc[article['question_label']== x, 'question_text'][0:1])
            #previously this was 'answer_number'
            answers = [article.loc[article['question_label']== x, 'answer_label']]
            answers.append([article.loc[article['question_label']== x, 'contributor_uuid']])
            answers.append([article.loc[article['question_label']== x, 'start_pos']])
            answers.append([article.loc[article['question_label']== x, 'end_pos']])
            answers.append([article.loc[article['question_label']== x, 'source_text_length']])
            #Change topic_name to answer_type when we get that feature request
            answers.append([article.loc[article['question_label'] == x, 'topic_name']])
            answers.append([article.loc[article['question_label'] == x, 'article_number']])
            answers.append([article.loc[article['question_label'] == x, 'schema_namespace']])
            answers.append([article.loc[article['question_label'] == x, 'target_text']])
            answers.append([article.loc[article['question_label'] == x, 'question_text']])
            answers.append([article.loc[article['question_label'] == x, 'answer_content']])

            array.append(answers)

            new_dict[x] = array
            #this is where krippendorf goes
        dict_of_article_df[i] = new_dict
    return dict_of_article_df

# Deprecated version, may be useful if we need to re-run the huge set of test cases
# def data_storer(path):
#     """Function that turns csv data. Input the path name for the csv file.
#     This will return a super dictionary that is used with other abstraction functions."""
#
#     data = pd.read_csv(path, encoding = 'utf-8')
#     article_nums = np.unique(data['taskrun_article_number'])
#     dict_of_article_df = dict()
#     for i in article_nums:d

#             answers = [article.loc[article['question_number']== x, 'answer_number']]
#             answers.append([article.loc[article['question_number']== x, 'contributor_id']])
#             answers.append([article.loc[article['question_number']== x, 'start_pos']])
#             answers.append([article.loc[article['question_number']== x, 'end_pos']])
#             answers.append([article.loc[article['question_number']== x, 'source_text_length']])
#             answers.append([article.loc[article['question_number'] == x, 'answer_type']])
#             array.append(answers)
#
#             new_dict[x] = array
#             #this is where krippendorf goes
#         dict_of_article_df[i] = new_dict
#     return dict_of_article_df

def filterDuplicatedAnswers(answersDF):
    return answersDF
#Abstraction functions for the data structure


def get_question_answers(data, article_num, question_num):
    question_labels = data[article_num][question_num][1][0]
    print('labs', question_labels)
    print(type(question_labels))
    question_nums = [parse(q, 'A') for q in question_labels]
    return question_nums

    #old version before we had to parse out the answer_num
    #return data[article_num][question_num][1][0]
def parse(label, field):
    aSpot = label.index(field)
    ansString = label[aSpot+1:]
    return int(ansString)

def get_question_userid(data, article_num, question_num):
    return data[article_num][question_num][1][1][0]


def get_question_start(data, article_num, question_num):
    return data[article_num][question_num][1][2][0]


def get_responses(article, question, csv_dict):
    return csv_dict[article][question][1:]


def get_user_count(article,question, csv_dict):
    return csv_dict[article][question][0]


def get_question_end(data, article_num, question_num):
    return data[article_num][question_num][1][3][0]

def get_text_length(data, article_num, question_num):
    return int(max(data[article_num][question_num][1][4][0]))
    #.iloc[0]

def get_num_users(data, article_num, question_num):
    return len(np.unique(get_question_userid(data, article_num, question_num)))

def get_question_type(data, article_num, question_num):
    return data[article_num][question_num][1][5][0].iloc[0]

def get_article_num(data, article):

    q  = min(data[article].keys())
    return data[article][q][1][6][0].iloc[0]


def get_namespace(data, article, question_num):
    return data[article][question_num][1][7][0].iloc[0]

def get_answer_texts(data, article_num, question_num):
    return data[article_num][question_num][1][8][0].tolist()

def get_question_text(data, article_num, question_num):
    return data[article_num][question_num][1][9][0].iloc[0]

def get_answer_content(data, article_num, question_num, answer_num):
    if answer_num == 'U' or answer_num == 'L' or answer_num == 'M' or answer_num == 'N/A':
        return answer_num

    answers = get_question_answers(data, article_num, question_num)
    index = finder(answers, answer_num)

    if index<0:
        return 'N/A'
    answer_contents = data[article_num][question_num][1][10][0]
    desired_content = answer_contents.tolist()[index]
    return desired_content

def finder(ser, a):
    if len(ser)<1:
        return -1
    for i in range(len(ser)):
            if ser[i]==a:
                    return i
    return -1

def get_type_hard(type, ques):
    ques = parse(ques, 'Q')
    #TODO:verify all of this against the schema
    typing_dict = {
        'Source relevance':
            {
                1: ['checklist', 7],
                2: ['checklist', 8],
                3: ['ordinal', 5]
            },
        #OLD
        'Science and Causality Questions for SSS Students V2':
            {
                5:['nominal', 1],
                6: ['checklist', 8],
                9:['ordinal', 4],
                10:['nominal', 1]
            },
        #OLD
        'Language Specialist V2':
            {
                1:['checklist',9],
                6:['checklist', 8],

            },
        'Language Specialist V3':
            {
                1:['checklist', 13],
                2:['ordinal', 5],
                3:['ordinal', 5],
                5:['ordinal', 5],
                6:['nominal', 8],
                7:['nominal',1],
                #TODO: is this ordinal?
                8:['ordinal', 4],
                9:['ordinal', 5],
                10: ['ordinal', 4],
                11: ['ordinal', 5],
                12: ['ordinal', 3],
                13: ['ordinal', 5],
                15: ['ordinal', 10],
                14: ['ordinal', 10]
            },
        'Confidence':
            {
                1:['ordinal', 3],
                2:['ordinal', 5],
                4:['ordinal', 3],
                5:['ordinal', 3],
                6:['nominal', 5],
                7:['ordinal', 3],
                8:['ordinal', 5],
                9:['ordinal', 5],
                10:['ordinal', 3],
                11:['ordinal', 4],
                12:['checklist', 4],
                13:['ordinal', 10],
                14:['ordinal', 10]
            },
        'Evidence Specialist':
            {
                2:['checklist', 3],
                3:['checklist', 8],
                #TODO: this is an interval quesiton, prob gonna get ignored l8r though
                4:['nominal', 1],
                5:['ordinal', 6],
                6:['ordinal', 5],
                7:['nominal', 3],
                8:['nominal', 1],
                9:['ordinal', 5],
                11:['ordinal', 3],
                12:['ordinal', 5],
                13:['ordinal', 5],
                14:['ordinal', 4],
                15:['ordinal', 10],
                16:['ordinal', 10]
            },
        'Beginner Reasoning Specialist Structured':
            {
                1:['checklist', 4],
                2:['checklist', 5],
                3:['checklist', 6],
                4:['ordinal', 3],
                5:['ordinal', 3],
                6:['checklist', 8],
                7:['ordinal', 5],
                8:['nominal', 1],
                #hardness
                9:['ordinal', 10],
                #confidence
                10:['ordinal', 10]
            },
        'Evidence':
            {
                5:['ordinal', 3],
                6:['checklist', 7],
                12:['nominal', 1]

            }

    }

    out = typing_dict[type][ques]
    return out[0], out[1]

def initRep(repCSV, data, source = 'specialist'):
    if repCSV != None:
        repDF = CSV_to_userid(repCSV)
    else:
        repDF = create_user_dataframe(data)
    return repDF
def initLast30(last30CSV, data):
    if last30CSV != None:
        last30 = CSV_to_last30(last30CSV)
    else:
        last30 = create_last30_dataframe(data)
    return last30
def cleanForUnitization(data, article_num, question_num):
    """Retuns dictionary of cleaned up data. Keys are Offsets, Lengths, Categories, Raters, and Ends
    and each value is an array of the data. DEPRECATED."""

    returnDict = dict()
    returnDict['Offsets'] = get_question_start(data, article_num,question_num).tolist()
    returnDict['Lengths'] = np.asarray((get_question_end(data, article_num, question_num)) -  np.asarray(get_question_start(data, article_num,question_num))).tolist()
    returnDict['Categories'] = get_question_answers(data, article_num, question_num).tolist()
    returnDict['Raters'] = get_question_userid(data, article_num, question_num).tolist()
    returnDict['Ends'] = np.asarray(get_question_end(data, article_num,question_num))
    return returnDict

def get_user_tuples(data, article_num, question_num):
    """Returns a dictionary of UserID as keys, and values being the tuples of start and ends
    of the highlights of each User."""
    returnDict = dict()
    users = get_question_userid(data, article_num, question_num)
    starts = get_question_start(data, article_num, question_num)
    ends = get_question_end(data, article_num, question_num)
    index = 0
    for u in users:
        returnDict[u] = (starts[index], ends[index])
        index += 1
    return returnDict

def get_user_arrays(data, article_num, question_num):
    """This gives a dictionary that has UserID's as keys, and their answer choices for the question
    as an array of 1's and 0's."""
    returnDict = dict()
    users = get_question_userid(data, article_num, question_num)
    answers = get_question_answers(data, article_num, question_num).tolist()
    index = 0
    for u in users:
        array = np.zeros(max(answers))
        array[answers[index]-1] = 1
        returnDict[u] = array
        index +=1
    return returnDict

def get_user_rep(id, repDF):
    if repDF.loc[repDF['Users']==id]['Questions'].iloc[0]<30:
        influence = .8
    else:
        influence = float(repDF.loc[repDF['Users']==id]['Influence'].iloc[0])
    return influence*50


#fetch_for_triage('SemanticsTriager1.3C2-2018-07-25T23.json')