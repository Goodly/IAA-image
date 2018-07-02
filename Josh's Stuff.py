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

def get_question_answer_ratios(dictionary):
     users_num = len(dictionary.keys())
     returnArray = np.zeros(len(list(dictionary.values())[0]))
     for a in dictionary.values():
         returnArray = returnArray + a
     return (returnArray/users_num).tolist()
     
 def test_threshold_matrix(array, num_of_users):
        # grade = "L"
        # return_array = []
        # index = 0
        # for i in array:
        #     if num_of_users <= 2:
        #         print("Not enough users")
        #         break
        #     if num_of_users == 3:
        #         if (i > 2/3):
        #             grade = "H"
        #     if num_of_users == 4:
        #         if (i > 1/4 and i < 3/4):
        #             grade = "M"
        #         elif (i >= 3/4):
        #             grade = "H"
        #     if num_of_users == 5:
        #         if i > 2/5 and i <4/5:
        #             grade = "M"
        #         elif (i >= 4/5):
        #             grade = "H"
        #     if num_of_users == 6:
        #         if i > 2/6 and i < 4/6:
        #             grade = "M"
        #         elif i >= 4/6:
        #             grade = "H"
        #     if num_of_users == 7:
        #         if i > 3/7 and i < 5/7:
        #             grade = "M"
        #         elif i >= 5/7:
        #             grade = "H"
        #     if num_of_users == 8:
        #         if i > 3/8 and i < 6/8:
        #             grade = "M"
        #         elif i >= 6/8:
        #             grade = "H"
        #     if num_of_users == 9:
        #         if i > 4/9 and i < 7/9:
        #             grade = "M"
        #         elif i >= 7/9:
        #             grade = "H"
        #     if num_of_users == 10:
        #         if i > 5/9 and i < 8/10:
        #             grade = "M"
        #         elif i >= 8/10:
        #             grade = "H"
        #     if grade == "H":
        #         return "H"
        #     else:
        #         index += 1
        #         return_array.append(grade)
        # 
        # if "M" in return_array: 
        #     return "M"
        # else:
        #     return "L"
    percentage = max(array)
    kappa = 50 *( 1- exp(-num_of_users/15))
    omega = 1/1+exp(-kappa*(percentage -.5))
    deriv = (kappa * exp(-kappa*(percentage)))/(exp(-kappa*(percentage-.5))+1)**2
    if (deriv < 1):
        return 'M'
    elif (x>=.5):
        return 'H'
    else:
        return 'L'
        
 
  def find_starts_ends_of_winner(data, article_num, question_num, user_arrays, answer_ratio_array):
      user_start_end = get_user_tuples(data, article_num, question_num)
      winner_pos = answer_ratio_array.index(max(answer_ratio_array))
          for k in user_arrays.keys():
                   if user_arrays[k][winner_pos] == 0:
                       del user_start_end[k]
          return user_start_end
 
 
 
 
 
 
 
 
 def find_agreement_scores_u(data, article_num, question_num):
        user_array_dict = get_user_arrays(data, article_num, question_num)
        ans_ratio = get_question_answer_ratios(user_array_dict)
        num_users = get_num_users(data,article_num, question_num)
        grade = test_threshold_matrix(ans_ratio, num_users)
        if grade == 'L':
            print("agreement too low")
            return 
        elif grade == 'M':
            print("return to sender")
            return
        else:
            return find_starts_ends_of_winner(data,article_num,question_num,user_array_dict, ans_ratio)
        