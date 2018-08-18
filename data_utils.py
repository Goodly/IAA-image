import pandas as pd
import numpy as np
from repScores import CSV_to_userid
from repScores import create_user_dataframe

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

def data_storer(path):
    """Function that turns csv data. Input the path name for the csv file.
    This will return a super dictionary that is used with other abstraction functions."""

    data = pd.read_csv(path, encoding = 'utf-8')
    article_nums = np.unique(data['article_sha256'])
    dict_of_article_df = dict()
    for i in article_nums:
        article =data[data['article_sha256'] == i]
        question_nums = np.unique(article['question_number'])
        new_dict = dict()
        for x in question_nums:
            array = []
            array.append(article.loc[article['question_number']== x, 'question_text'][0:1])

            answers = [article.loc[article['question_number']== x, 'answer_number']]
            answers.append([article.loc[article['question_number']== x, 'contributor_uuid']])
            answers.append([article.loc[article['question_number']== x, 'start_pos']])
            answers.append([article.loc[article['question_number']== x, 'end_pos']])
            answers.append([article.loc[article['question_number']== x, 'source_text_length']])
            #Change topic_name to answer_type when we get that feature request
            answers.append([article.loc[article['question_number'] == x, 'topic_name']])
            answers.append([article.loc[article['question_number'] == x, 'article_number']])
            answers.append([article.loc[article['question_number'] == x, 'namespace']])
            answers.append([article.loc[article['question_number'] == x, 'target_text']])
            answers.append([article.loc[article['question_number'] == x, 'question_text']])
            answers.append([article.loc[article['question_number'] == x, 'answer_content']])

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

#Abstraction functions for the data structure
def get_question_answers(data, article_num, question_num):
    return data[article_num][question_num][1][0]


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

    answers = get_question_answers(data, article_num, question_num).tolist()

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
    #TODO:verify all of this against the schema
    typing_dict = {
        'Source relevance':
            {
                1: ['checklist', 7],
                2: ['checklist', 8],
                3: ['ordinal', 5]
            },
        'Science and Causality Questions for SSS Students V2':
            {
                5:['nominal', 1],
                6: ['checklist', 8],
                9:['ordinal', 4],
                10:['nominal', 1]
            },
        'Language Specialist V2':
            {
                1:['checklist',9],
                6:['checklist', 8],

            },
        'CausalitySpecialist_2018_07_19':
            {
                5:[]
            }

    }

    out = typing_dict[type][ques]
    return out[0], out[1]

def initRep(repCSV, data, source = 'specialist'):
    if repCSV != None:
        repDF = CSV_to_userid(repCSV)
    else:
        repDF = create_user_dataframe(data, source = source)

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
    #print(repDF.loc[repDF['Users']==id]['Score'])
    if repDF.loc[repDF['Users']==id]['Questions'].iloc[0]<30:
        influence = .8
    else:
        influence = float(repDF.loc[repDF['Users']==id]['Influence'].iloc[0])
    return influence*50


#fetch_for_triage('SemanticsTriager1.3C2-2018-07-25T23.json')