from math import exp
def evalThresholdMatrix(percentage, num_of_users, scale = 1.0, q = 1, giveMin = False):
    """

    :param percentage: percentage agreement
    :param num_of_users: number of users
    :param scale: scales percentage, higher scale is a friendlier function, lower scale is stricter
    :param q: adjusting q adjusts the midpoint of the logistic curve, higher Qs willyield more H,
    but can make M almost never return
    :return: a code denoting the success of the inputs in this funciton, 'U' means too few leaders, while
    H, M, and L denote the degree  of agreement
    """
    out = 0
    if num_of_users<3:
        out =  'U'
    else:
        percentage = percentage*scale
        kappa = 2+1 *(1 - exp((-num_of_users)/50))
        #omega = 1/1+exp(-kappa*(percentage -.5))
        #print(kappa, percentage, q)
        derivOld = ((kappa * q*exp(-kappa*(percentage)))/(q*(exp(-kappa*(percentage-.5))+1))**2)*5.7
        #for typing it into internet equation solvers:
        #(k * e^(-k*(p))/(e^(-k*(p-0.5))+1)^2)*5.7
        deriv = logistic_derivative(percentage, kappa)
        #print(deriv, derivOld)
#        assert deriv == derivOld
        if (deriv > 1):
            out =  'M'
        elif (percentage >.5):
            out =  'H'
        else:
            out =  'L'
    if giveMin:
        if out == 'U':
            out = (out, 'U')
        else:
            minPass = findMinPass(percentage, num_of_users, scale, q)
            out = (out, minPass)
    return out

def logistic_derivative(percentage, kappa, n = 0):
    q = 1
    #print(kappa, percentage)
    deriv = ((kappa * exp(kappa * (percentage-.5))) / ((exp(kappa * (percentage - .5)) + 1)) ** 2)
    return deriv

def parabThreshold(percentage, num_of_users, scale = 1, q = 1):
    #lower Q is easier, higher q is stricter and has more range for 'M' outputs
    #I don't think it should ever be too far below .8
    #WARNING: ACCEPTS percentages below 50% with more than 8 users, don't try to use
    # this on specialist interace
    #ALSO This is super strict on low numbers of users
    if num_of_users<3:
        return 'U'
    percentage = percentage*scale
    k = num_of_users**(num_of_users/(.6*q*num_of_users))

    determiner = (1.5-k*(percentage-.55+(k/(55*q*num_of_users)))**2)
    #print(determiner)
    if determiner>1:
        return 'M'
    elif percentage >(.5-k/(55*q*num_of_users)) and percentage >(.5-k/(55*q*10)):
        return 'H'
    else:
        return 'L'

#TODO: make a cache so this happens faster
def findMinPass(percentage, num_users, scale, q):
    if evalThresholdMatrix(percentage, num_users, scale, q) == 'H':
        if evalThresholdMatrix(percentage-.1, num_users, scale, q) != 'H':
            #print(percentage, num_users)
            return percentage
        return findMinPass(percentage-.1, num_users, scale, q)
    #print(percentage)
    return findMinPass(percentage+.1, num_users, scale, q)
#def findMinPass(equation, percentage, kappa, scale, num_users = 5):

    # val = equation(percentage, kappa, num_users)
    # if percentage<.5:
    #     return findMinPass(equation, .7, kappa, num_users)
    # elif val<=1:
    #     if equation(percentage-.1, kappa, num_users)>1:
    #         return percentage/scale
    #     else:
    #         return findMinPass(equation, percentage-.01,kappa, scale, num_users)
    # elif val > 1:
    #     return findMinPass(equation, percentage+.01, kappa, scale, num_users)
#    if


def checkThreshold():
    for i in range(1,10):
        for u in range(3,11):
            p = i/10
            print(str(p)+"%", u, 'users')
            print(evalThresholdMatrix(p,u))
            print('1.4',evalThresholdMatrix(p, u, scale=1.4))
            print('1.7', evalThresholdMatrix(p,u,scale=1.7))
            #print(parabThreshold(p, u, 1.7, .85))
            # print(evalThresholdMatrix(p, u, 1.4))
            # print(evalThresholdMatrix(p, u, 1.4,1.2))
            # print(evalThresholdMatrix(p, u, 1.4, 1.2))
#checkThreshold()