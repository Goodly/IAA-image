from data_utils import *
from ThresholdMatrix import *
from math import exp



def create_user_dataframe(data,csvPath = None):
    """This function creates a DataFrame of User ID's, Reputation Scores, and number of questions answered."""
    if csvPath:
        data1 = CSV_to_userid(csvPath)
    else:
        data1 = pd.DataFrame(columns= ['Users', 'Score' ,'Questions','Influence'] )
    for article_num in data.keys():
        for question_num in data[article_num].keys():
            users_q = get_question_userid(data, article_num, question_num)
            for ids in users_q:
                ids = int(ids)
                if ids not in data1.loc[:, 'Users'].tolist():
                    data1 = data1.append({"Users" :ids, "Score" :5, "Questions": 1, "Influence":1}, ignore_index = True)
    return data1
def do_rep_calculation_nominal(userID, answers, answer_choice, data, checkListScale = 1):
    """Using the same dataframe of userIDs, rep scores, and number of questions, changes the vals of the dataframe
    such that if the user in the list of USERID gets their answer right, they add 1 to their score, and 0 if they are
    wrong."""
    if type(answer_choice) == str:
        return 0
    checked = checkDuplicates(userID, answers)
    print(checked)
    for t in checked:
        user = t[1]
        answer = t[0]
        print(answer, answer_choice, user)
        if (answer == answer_choice):
            do_math(data, user, checkListScale)
        else:
            do_math(data, user, 0)
def do_rep_calculation_ordinal(userID, answers, answer_aggregated ,num_of_choices, data):
    """Using the same dataframe of userIDs, rep scores, and number of questions, changes the vals of the dataframe
    such that the they recieve the distance from the average answer chosen as a ratio of 0 to 1,
    and that is added to their rep score."""
    if type(answer_aggregated) == str:
        return 0
    checked = checkDuplicates(userID, answers)
    answers_passed = list()
    for i in checked:
        answers_passed.append(checked[i][1])
    answer_choice = np.mean(answers_passed)
    for t in checked:
        user = t[1]
        answer = t[0]
        points = (1 - abs(answer_choice - answer ) /num_of_choices)
        do_math(data, user, points)

def checkDuplicates(userID, answers):
    checked = []
    for i in range(len(answers)):
        if (answers[i], userID[i]) not in checked:
            checked.append((answers[i], userID[i]))
    return checked
def do_math(data, userID, reward):
    """This function takes in the points added to one user and changes the dataframe to update that one user's score
    using the equations set for calculating reputation."""
    user = data.loc[data['Users' ]== userID]
    print('inDoMath uID', userID)
    print()
    r = float(user['Score'].iloc[0])
    n = float(user['Questions'].iloc[0])
    q_score = 10* (1 - exp(-n/.7))
    points = r * n / q_score
    points = points + reward
    n = n+ 1
    q_score = 10 * (1 - exp(-n/.7))
    data.loc[data['Users'] == userID,'Questions'] = n
    data.loc[data['Users'] == userID, 'Score'] = (points / n) * q_score
    data.loc[data['Users'] == userID, 'Influence'] = 2 / (1 + 1*exp(-.7*(points / n) * q_score + 5))
    print(reward)
    print(data)

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
    return pd.read_csv(path, index_col=False).loc[:, ['Users', 'Score', 'Questions','Influence']]
