from data_utils import *
from ThresholdMatrix import *
from math import exp
import numpy as np
import pandas as pd



def create_user_dataframe(data, csvPath=None):
    """This function creates a DataFrame of User ID's, Reputation Scores, and number of questions answered."""
    if csvPath:
        data1 = CSV_to_userid(csvPath)
    else:
        data1 = pd.DataFrame(columns=['Users', 'Score', 'Questions', 'Influence'])
    for article_num in data.keys():
        for question_num in data[article_num].keys():
            users_q = get_question_userid(data, article_num, question_num)
            for ids in users_q:
                if ids not in data1.loc[:, 'Users'].tolist():
                    data1 = data1.append({"Users": ids, "Score": 5, "Questions": 1, "Influence": 1}, ignore_index=True)
    return data1


def create_last30_dataframe(data, csvPath=None):
    if csvPath:
        data1 = CSV_to_last30(csvPath)
    else:
        data1 = pd.DataFrame(columns=['Users', 'Index'] + list(range(30)))
    for article_num in data.keys():
        for question_num in data[article_num].keys():
            users_q = get_question_userid(data, article_num, question_num)
            for ids in users_q:
                if ids not in data1.loc[:, 'Users'].tolist():
                    data1 = data1.append({"Users": ids, "Index": 0}, ignore_index=True)
    return data1


def do_rep_calculation_nominal(userID, answers, answer_choice, highlight_answer, starts, ends, article_length, data,
                               last30,checkListScale=1):
    """Using the same dataframe of userIDs, rep scores, and number of questions, changes the vals of the dataframe
    such that if the user in the list of USERID gets their answer right, they add 1 to their score, and 0 if they are
    wrong."""
    if type(answer_choice) == str or type(highlight_answer) == str:
        return 0
    checked, int_users = checkDuplicates(answers, userID, starts, ends, article_length)
    print(checked)
    print(int_users)
    highlight_answer_array = np.zeros(article_length)
    winners = []
    for t in checked:
        user = t[1]
        answer = t[0]
        print(answer, answer_choice, user)
        if (answer == answer_choice):
            do_math(data, last30, user, checkListScale)
            winners.append(user)
        else:
            do_math(data, user, 0)
    for h in highlight_answer:
        highlight_answer_array[h] = 1
    for x in int_users:
        if x in winners:
            highlight = np.array(int_users[x])
            score = 1 - np.sum(np.absolute(highlight_answer_array - highlight)) / article_length
            do_math(data, last30, x, score)


def gaussian_mean(answers):
    result = []
    std = np.std(answers)
    mean = np.mean(answers)
    total = 0
    for i in answers:
        gauss = 1 / (std * np.sqrt(2 * np.pi)) * np.exp(-0.5 * ((i - mean) / std) ** 2)
        result.append(i * (gauss * 10) ** 2)
        total += (gauss * 10) ** 2
    print(result)
    print(answers)
    print(np.mean(answers))
    print(sum(result) / total)
    return sum(result) / total


def do_rep_calculation_ordinal(userID, answers, answer_aggregated, num_of_choices, highlight_answer, starts, ends,
                               article_length, data, last30):
    """Using the same dataframe of userIDs, rep scores, and number of questions, changes the vals of the dataframe
    such that the they receive the distance from the average answer chosen as a ratio of 0 to 1,
    and that is added to their rep score."""
    print(answer_aggregated)
    if type(answer_aggregated) == str or type(highlight_answer) == str:
        return 0
    checked, int_users = checkDuplicates(answers, userID, starts, ends, article_length)
    answers_passed = list()
    highlight_answer_array = np.zeros(article_length)
    score_dict = {}
    print(checked)
    for i in checked:
        answers_passed.append(i[1])
    answer_choice = gaussian_mean(answers)

    for h in highlight_answer:
        print(h)
        highlight_answer_array[h] = 1

    for t in checked:
        user = t[1]
        answer = t[0]
        points = (1 - abs(answer_choice - answer) / num_of_choices) ** 3
        do_math(data, last30, user, points)
        score_dict[user] = points
    for x in int_users:
        points = score_dict[x]
        highlight = np.array(int_users[x])

        score = points * (1 - np.sum(np.absolute(highlight_answer_array - highlight)) / article_length)
        do_math(data, last30, x, score)


def checkDuplicates(answers, userID, starts, ends, article_length):
    checked = []
    int_users = {}

    for i in range(len(answers)):
        if [answers[i], userID[i], int(starts[i]), int(ends[i])] not in checked:
            checked.append([answers[i], userID[i], int(starts[i]), int(ends[i])])
    for x in checked:
        article_array = np.zeros(article_length).tolist()
        if x[0] not in int_users.keys():
            print("HELLO THERE", x[2], x[3])
            article_array[x[2]:x[3] + 1] = np.ones(x[3] - x[2] + 1).tolist()
            int_users[x[0]] = article_array
        else:
            article_array = int_users[x[0]]
            article_array[x[2]:x[3] + 1] = np.ones(x[3] - x[2] + 1).tolist()
            int_users[x[0]] = article_array

    return checked, int_users


def do_math(data, last30, userID, reward):
    """This function takes in the points added to one user and changes the dataframe to update that one user's score
    using the equations set for calculating reputation."""
    oldlast30mean = np.mean(np.array(last30.loc[last30['Users'] == userID, range(30)]))
    oldlast30q_score = len(np.array(last30.loc[last30['Users'] == userID, range(30)]))
    oldlast30score = oldlast30mean * oldlast30q_score

    user = data.loc[data['Users'] == userID]
    index = last30.loc[last30['Users'] == userID, 'Index']
    last30.loc[last30['Users'] == userID, index] = reward
    last30user = last30.loc[last30['Users'] == userID, range(30)]
    last30mean = np.mean(np.array(last30user.dropna(axis=1)))
    last30q_score = len(np.array(last30user.dropna(axis=1)))
    last30score = last30mean * last30q_score

    # print('inDoMath uID', userID)
    # print()
    r = float(user['Score'].iloc[0])*2 - oldlast30score
    n = float(user['Questions'].iloc[0])
    q_score = 10 * (1 - exp(-n / .7))
    points = r * n / q_score
    points = points + reward
    n = n + 1
    q_score = 10 * (1 - exp(-n / .7))
    data.loc[data['Users'] == userID, 'Questions'] = n
    data.loc[data['Users'] == userID, 'Score'] = ((points / n) * q_score + last30score)/2
    data.loc[data['Users'] == userID, 'Influence'] = 2 / (1 + 1 * exp(-.7 * ((points / n) * q_score + last30score)/2+ 5))

    # print(reward)
    # print(data)


def calc_influence(data, userID):
    """Taking in a list of UserID's, this will take the repuation score of each User and output a list of their influence
    based on their reputation score."""
    return_vals = list()
    for u in userID:
        r = data.loc[data['Users'] == u]['Score']
        inf = 2 / (1 + exp(-r + 5))
        return_vals.append(inf)
    return return_vals


def userid_to_CSV(dataframe):
    """This function will save the User Rep Score dataframe as UserRepScores.csv"""
    dataframe.to_csv("UserRepScores.csv")


def CSV_to_userid(path):
    """This function will take in the path name of the UserRepScore.csv and output the dataframe corresponding."""
    return pd.read_csv(path, index_col=False).loc[:, ['Users', 'Score', 'Questions', 'Influence']]


def last30_to_CSV(dataframe):
    """This function will save the last 30 questions rep points dataframe as last30.csv"""
    dataframe.to_csv("last30.csv")


def CSV_to_last30(path):
    """This function opens the csv of the last 30 questions rep points dataframe as last30.csv"""
    return pd.read_csv(path, index_col=False).loc[:, ['Users', 'Index'] + list(range(30))]
