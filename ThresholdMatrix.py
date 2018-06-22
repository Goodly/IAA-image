def evalThresholdMatrix(i, num_of_users):
    grade = "L"
    return_array = []
    index = 0
    if num_of_users <= 2:
        #print("Not enough users")
        grade = 'U'
    if num_of_users == 3:
        if (i > 2/3):
            grade = "H"
    if num_of_users == 4:
        if (i > 1/4 and i < 3/4):
            grade = "M"
        elif (i >= 3/4):
            grade = "H"
    if num_of_users == 5:
        if i > 2/5 and i <4/5:
            grade = "M"
        elif (i >= 4/5):
                grade = "H"
    if num_of_users == 6:
        if i > 2/6 and i < 4/6:
            grade = "M"
        elif i >= 4/6:
            grade = "H"
    if num_of_users == 7:
        if i > 3/7 and i < 5/7:
            grade = "M"
        elif i >= 5/7:
            grade = "H"
    if num_of_users == 8:
        if i > 3/8 and i < 6/8:
            grade = "M"
        elif i >= 6/8:
            grade = "H"
    if num_of_users == 9:
        if i > 4/9 and i < 7/9:
            grade = "M"
        elif i >= 7/9:
            grade = "H"
    if num_of_users == 10:
        if i > 5/9 and i < 8/10:
            grade = "M"
        elif i >= 8/10:
            grade = "H"
    if grade == "H":
        return "H"
    else:
        index += 1
        return_array.append(grade)
    if "M" in return_array:
        return "M"
    else:
        return "L"
