
def find_agreement_scores_u(data, article_num, question_num):
    user_array_dict = get_user_arrays(data, article_num, question_num)
    ans_ratio = get_question_answer_ratios(user_array_dict)
    num_users = get_num_users(data ,article_num, question_num)
    grade = test_threshold_matrix(ans_ratio, num_users)
    if grade == 'L':
        print("agreement too low")
        return
    elif grade == 'M':
        print("return to sender")
        return
    else:
        return find_starts_ends_of_winner(data ,article_num ,question_num ,user_array_dict, ans_ratio)
def create_user_dataframe(data):
    """This function creates a DataFrame of User ID's, Reputation Scores, and number of questions answered."""
    data1 = pd.DataFrame(columns= ['Users', 'Score' ,'Questions'] )
    for article_num in data.keys():
        for question_num in data[article_num].keys():
            users_q = get_question_userid(data, article_num, question_num)
            for ids in users_q:
                if ids not in data1.loc[: ,'Users']:
                    data1 = data1.append({"Users" :ids, "Score" :5, "Questions": 1}, ignore_index = True)
    return data1
def do_the_calculation_nominal(userID, answers, answer_choice, data):
    """Using the same dataframe of userIDs, rep scores, and number of questions, changes the vals of the dataframe
    such that if the user in the list of USERID gets their answer right, they add 1 to their score, and 0 if they are
    wrong."""
    tups = list()
    for ids in userID:
        for a in answers:
            pair = (ids, a)
            if pair not in tups:
                tups.append(pair)
    for t in tups:
        user = t[0]
        answer = t[1]
        if (answer == answer_choice):
            do_math(data, user, 1)
        else:
            do_math(data, user, 0)
def do_the_calculation_ordinal(userID, answers, answer_aggregated ,num_of_choices, data):
    """Using the same dataframe of userIDs, rep scores, and number of questions, changes the vals of the dataframe
    such that the they recieve the distance from the average answer chosen as a ratio of 0 to 1,
    and that is added to their rep score."""
    tups = list()
    for ids in userID:
        for a in answers:
            pair = (ids, a)
            if pair not in tups:
                tups.append(pair)
    answer_choice = np.mean(answer_aggregated)
    for t in tups:
        user = t[0]
        answer = t[1]
        points = (1 - abs(answer_choice - answer ) /num_of_choices)
        do_math(data, user, points)
def do_math(data, userID, reward):
    """This function takes in the points added to one user and changes the dataframe to update that one user's score
    using the equations set for calculating reputation."""
    user = data.loc[data['Users' ]== userID]
    r = user['Score']
    n = user['Questions']
    q_score = 1 0* (1 - exp(-n))
    points = r * n / q_score
    points = points + reward
    n = n+ 1
    q_score = 10 * (1 - exp(-n))
    user['Questions'] = n
    user['Score'] = (points / n) * q_score


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
    dataframe.to_csv("UserRepScores")


def CSV_to_userid(path):
    """This function will take in the path name of the UserRepScore.csv and output the dataframe corresponding."""
    return pd.read_csv(path, index_col=False).loc[:, ['Users', 'Score', 'Questions']]
