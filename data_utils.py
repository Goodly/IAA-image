import pandas as pd
import numpy as np


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
    return max(data[article_num][question_num][1][4][0])
    #.iloc[0]

def get_num_users(data, article_num, question_num):
    return len(np.unique(get_question_userid(data, article_num, question_num)))

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

# def get_question_answer_ratios(dictionary):
#     """By inputting the dictionary outputted by get_user_arrays, this function
#      will return an array of all the answer choices as percentage agreement."""
#      users_num = len(dictionary.keys())
#      returnArray = np.zeros(len(list(dictionary.values())[0]))
#      for a in dictionary.values():
#          returnArray = returnArray + a
#      return (returnArray/users_num).tolist()
#
# def test_threshold_matrix(array, num_of_users):
#     """By putting in the array returned by get_question_answer_ratios and the number of users
#     for a specific question, this function will return whether or not people agree L - Low, M - Medium,
#     or H - High."""
#     grade = "L"
#     return_array = []
#     index = 0
#     for i in array:
#         if num_of_users <= 2:
#             print("Not enough users")
#             break
#         if num_of_users == 3:
#             if (i > 2/3):
#                 grade = "H"
#         if num_of_users == 4:
#             if (i > 1/4 and i < 3/4):
#                 grade = "M"
#             elif (i >= 3/4):
#                 grade = "H"
#         if num_of_users == 5:
#             if i > 2/5 and i <4/5:
#                 grade = "M"
#             elif (i >= 4/5):
#                 grade = "H"
#         if num_of_users == 6:
#             if i > 2/6 and i < 4/6:
#                 grade = "M"
#             elif i >= 4/6:
#                 grade = "H"
#         if num_of_users == 7:
#             if i > 3/7 and i < 5/7:
#                 grade = "M"
#             elif i >= 5/7:
#                 grade = "H"
#         if num_of_users == 8:
#             if i > 3/8 and i < 6/8:
#                 grade = "M"
#             elif i >= 6/8:
#                 grade = "H"
#         if num_of_users == 9:
#             if i > 4/9 and i < 7/9:
#                 grade = "M"
#             elif i >= 7/9:
#                 grade = "H"
#         if num_of_users == 10:
#             if i > 5/9 and i < 8/10:
#                 grade = "M"
#             elif i >= 8/10:
#                 grade = "H"
#         if grade == "H":
#             return "H"
#         else:
#             index += 1
#             return_array.append(grade)
#
#     if "M" in return_array:
#         return "M"
#     else:
#         return "L"
# def find_starts_ends_of_winner(data, article_num, question_num, user_arrays, answer_ratio_array):
#     """Helper function for the find_agreement_scores functions."""
#     user_start_end = get_user_tuples(data, article_num, question_num)
#     winner_pos = answer_ratio_array.index(max(answer_ratio_array))
#     for k in user_arrays.keys():
#         if user_arrays[k][winner_pos] == 0:
#             del user_start_end[k]
#     return user_start_end
#
# def find_agreement_scores_u(data, article_num, question_num):
#     """By inputting the super dictionary, article number and question number, this function
#     will return a dicitonary of UserID's as keys and Highlight tuples as values for each user that agreed
#     with the most agreed upon answer."""
#     user_array_dict = get_user_arrays(data, article_num, question_num)
#     ans_ratio = get_question_answer_ratios(user_array_dict)
#     num_users = get_num_users(data,article_num, question_num)
#     grade = test_threshold_matrix(ans_ratio, num_users)
#     if grade == 'L':
#         print("agreement too low")
#         return
#     elif grade == 'M':
#         print("return to sender")
#         return
#     else:
#         return find_starts_ends_of_winner(data,article_num,question_num,user_array_dict, ans_ratio)
# def find_agreement_scores_c(data, article_num, question_num):
#     """By inputting the super dictionary, article number and question number, this function
#     will return a dicitonary of UserID's as keys and answer arrays for each user that agreed
#     with the most agreed upon answer."""
#     user_array_dict = get_user_arrays(data, article_num, question_num)
#     ans_ratio = get_question_answer_ratios(user_array_dict)
#     num_users = get_num_users(data,article_num, question_num)
#     grade = test_threshold_matrix(ans_ratio, num_users)
#     if grade == 'L':
#         print("agreement too low")
#         return
#     elif grade == 'M':
#         print("return to sender")
#         return
#     else:
#         index = ans_ratio.index(max(ans_ratio))
#         for k in user_array_dict.keys():
#             if user_array_dict[k][index] == 0:
#                 del user_array_dict[k]
#         return user_array_dict
