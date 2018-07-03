from math import exp
def evalThresholdMatrix(percentage, num_of_users):

    kappa = 2+1 *(1 - exp((-num_of_users)/50))

    q = 1
    #omega = 1/1+exp(-kappa*(percentage -.5))
    deriv = ((kappa * q*exp(-kappa*(percentage)))/(q*(exp(-kappa*(percentage-.5))+1))**2)*5.7
    if (deriv > 1):
        return 'M'
    elif (percentage >.5):
        return 'H'
    else:
        return 'L'
