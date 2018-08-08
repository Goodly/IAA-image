import pandas as pd
import numpy as np

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

    data = pd.read_csv(path)
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
            answers.append([article.loc[article['question_number'] == x, 'answer_type']])
            array.append(answers)

            new_dict[x] = array
            #this is where krippendorf goes
        dict_of_article_df[i] = new_dict
    return dict_of_article_df


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
#Retuns dictionary of cleaned up data
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