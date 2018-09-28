import Krippendorff
import csv
import pandas as pd
import numpy as np



#This is the new IAA sans DKpro


path = './pe_data/pe_data_test.csv'

test_path = './PE_test_data_120.csv'
test_data = data_storer(test_path)

# Creates user array of 1's and 0's for annotations
def create_user_arr(article, question, length, data, user_tuples):
    #anno_data = get_user_tuples(data, article, question)
    anno_list = np.zeros(length)
    #pos_tuples = anno_data[user]
    for pt in user_tuples:
        for i in np.arange(pt[0],pt[1]):
            i = i - 1
            anno_list[i] = 1
    return anno_list

#Functions used for coding percentage agreements on a specific question

  #This function returns a dictionary with keys as user id's and the values as the array of answer choices, where 1 is yes and 0 is no
  def get_user_arrays(data, article_num, question_num):
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

  #This function takes in a dictionary outputted by get_user_arrays to give an array of the percentage agreement per answer choice.
  def get_question_answer_ratios(dictionary):
    users_num = len(dictionary.keys())
    returnArray = np.zeros(len(list(dictionary.values())[0]))
    for a in dictionary.values():
        returnArray = returnArray + a
    return returnArray/users_num




#Function that turns csv data
def data_storer(path):
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
    return data[article_num][question_num][1][4][0].iloc[0]

def get_num_users(data, article_num, question_num):
    return len(np.unique(get_question_userid(data, article_num, question_num)))

#Retuns dictionary of cleaned up data
def cleanForUnitization(data, article_num, question_num):
    returnDict = dict()
    returnDict['Offsets'] = get_question_start(data, article_num,question_num).tolist()
    returnDict['Lengths'] = np.asarray((get_question_end(data, article_num, question_num)) -  np.asarray(get_question_start(data, article_num,question_num)))
    returnDict['Categories'] = get_question_answers(data, article_num, question_num).tolist()
    returnDict['Raters'] = get_question_userid(data, article_num, question_num).tolist()
    returnDict['Ends'] = np.asarray(get_question_end(data, article_num,question_num))
    return returnDict

def get_user_tuples(data, article_num, question_num):
    returnDict = dict()
    users = get_question_userid(data, article_num, question_num)
    starts = get_question_start(data, article_num, question_num)
    ends = get_question_end(data, article_num, question_num)
    index = 0
    for u in users:
        returnDict[u] = (starts[index], ends[index])
        index += 1
    return returnDict