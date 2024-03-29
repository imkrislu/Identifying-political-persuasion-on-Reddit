from sklearn.model_selection import train_test_split
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_classif
from sklearn.feature_selection import chi2
import numpy as np
import argparse
import sys
import os
import csv
from sklearn.metrics import confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.svm import LinearSVC
from sklearn.svm import SVC
from sklearn.model_selection import KFold
from scipy import stats
from sklearn.datasets import load_iris
from sklearn.model_selection import cross_val_score
from sklearn.tree import DecisionTreeClassifier

def accuracy( C ):
    ''' Compute accuracy given Numpy array confusion matrix C. Returns a floating point value '''
    dividend = np.sum(np.sum(C, axis=1))
    return np.true_divide(np.sum(np.diag(C)), dividend, where=dividend!=0)

def recall( C ):
    ''' Compute recall given Numpy array confusion matrix C. Returns a list of floating point values '''
    dividend = np.sum(C, axis=1)
    return np.true_divide(np.diag(C), dividend, where=dividend!=0).tolist()

def precision( C ):
    ''' Compute precision given Numpy array confusion matrix C. Returns a list of floating point values '''
    dividend = np.sum(C, axis=0)
    return np.true_divide(np.diag(C), dividend, where=dividend!=0).tolist()

def classBonus(filename):
    ''' This function performs experiment Bonus explores all 
        the classifiers
    
    Parameters
       filename : string, the name of the npz file from Task 2

    '''
    decisionTreeResult = []
    AdaBoostResult = []
    MLPResult = []
    RandomForResult = []
    # load data
    data = np.load(filename)
    data = data['arr_0']

    # getting y value
    X = data[:,:-1]
    y = data[:,-1]

    # splitting data into test and training 20%,80% 
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=66)
    

    maxDep = range(1, 16)
    # Random Forest performance may be different for each train
    for depth in maxDep:
        print("Depth: " + str(depth))

        model = RandomForestClassifier(max_depth=depth, n_estimators=10)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        C = confusion_matrix(y_test, y_pred)
        print(C)
        output = ["RandomForestClassifier"] + [depth] + [accuracy(C)] + recall(C) + precision(C) + np.ravel(C).tolist()
        RandomForResult.append(output)

    aList = [1, 0.8, 0.6, 0.4, 0.2, 0.1, 0.05, 0.025, 0.01]
    # MLP performance may be different for each train
    for alpha in aList:
        print("Alpha: " + str(alpha))

        model = MLPClassifier(alpha=0.05)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        C = confusion_matrix(y_test, y_pred)
        print(C)
        output = ["MLPClassifier"] + [alpha] + [accuracy(C)] + recall(C) + precision(C) + np.ravel(C).tolist()
        MLPResult.append(output)
    
    learnRate = [0.1, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
    # AdaBoost 
    for rate in learnRate:
        print("learnRate: " + str(learnRate))

        model = AdaBoostClassifier(learning_rate=rate)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        C = confusion_matrix(y_test, y_pred)
        print(C)
        output = ["AdaBoost"] + [rate] + [accuracy(C)] + recall(C) + precision(C) + np.ravel(C).tolist()
        AdaBoostResult.append(output) 

    maxFeatList = ['log2', 'sqrt', None]
    # Decision Tree 
    for feat in maxFeatList:
        print("max Feats: " + str(feat))

        model = DecisionTreeClassifier(random_state=66, max_features=feat)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        C = confusion_matrix(y_test, y_pred)
        print(C)
        output = ["Decision Tree"] + [feat] + [accuracy(C)] + recall(C) + precision(C) + np.ravel(C).tolist()
        decisionTreeResult.append(output)

    bestAccuracy = -1

    result = [decisionTreeResult, AdaBoostResult, MLPResult, RandomForResult]
    with open('a1_bonus.csv', 'w', newline='') as csvFile:
        csvWriter = csv.writer(csvFile, delimiter=',')
        for r in result:
            csvWriter.writerows(r)


def class32(X_train, X_test, y_train, y_test,iBest):
    ''' This function performs experiment 3.2
    
    Parameters:
       X_train: NumPy array, with the selected training features
       X_test: NumPy array, with the selected testing features
       y_train: NumPy array, with the selected training classes
       y_test: NumPy array, with the selected testing classes
       i: int, the index of the supposed best classifier (from task 3.1)  

    Returns:
       X_1k: numPy array, just 1K rows of X_train
       y_1k: numPy array, just 1K rows of y_train
   '''
    dataSize = [1000, 5000, 10000, 15000, 20000]
    # choose best model
    if iBest == 1:
        model = LinearSVC(max_iter=10000)
    elif iBest == 2:
        model = SVC(max_iter=10000, gamma=2)
    elif iBest == 3:
        model = RandomForestClassifier(max_depth=5, n_estimators=10)
    elif iBest == 4:
        model = MLPClassifier(alpha=0.05)
    else:
        model = AdaBoostClassifier()

    # accuracy
    accur = []
    for size in dataSize:
        model.fit(X_train[:size], y_train[:size])
        C = confusion_matrix(model.predict(X_test), y_test)
        accur.append(accuracy(C))
    with open('a1_3.2.csv', "w", newline='') as csvFile:
        csvWriter = csv.writer(csvFile, delimiter=',')
        csvWriter.writerow(accur)

    X_1k = np.array(X_train[:dataSize[0]]) 
    y_1k = np.array(y_train[:dataSize[0]])
    return (X_1k, y_1k)
    
def class33(X_train, X_test, y_train, y_test, i, X_1k, y_1k):
    ''' This function performs experiment 3.3
    
    Parameters:
       X_train: NumPy array, with the selected training features
       X_test: NumPy array, with the selected testing features
       y_train: NumPy array, with the selected training classes
       y_test: NumPy array, with the selected testing classes
       i: int, the index of the supposed best classifier (from task 3.1)  
       X_1k: numPy array, just 1K rows of X_train (from task 3.2)
       y_1k: numPy array, just 1K rows of y_train (from task 3.2)
    '''
    kList = {5, 10, 20, 30, 40, 50}
    csvResult = []
    pval1 = []
    pval32 = []

    # find the best k features p values for 1k and 32k
    for i in kList:
        selector = SelectKBest(f_classif, k=i) 
        X_new = selector.fit_transform(X_1k, y_1k)
        pp = sorted(selector.pvalues_)
        pval1.append(pp[:i])
    print(pval1)

    for i in kList:
        selector = SelectKBest(f_classif, k=i) 
        X_new = selector.fit_transform(X_train, y_train)
        pp = sorted(selector.pvalues_)
        pval32.append(pp[:i])
        csvResult.append([i] + pp)
    print(pval32)

    # 1k and 32k with 5 features
    selector = SelectKBest(f_classif, k=5) 
    X_train1k = selector.fit_transform(X_1k, y_1k)
    X_test1k = selector.transform(X_test)
    print(X_train1k)

    selector = SelectKBest(f_classif, k=5) 
    X_train32k = selector.fit_transform(X_train, y_train)
    X_test32k = selector.transform(X_test)
    print(X_train32k)

    if iBest == 1:
        model = LinearSVC(max_iter=10000)
    elif iBest == 2:
        model = SVC(max_iter=10000, gamma=2)
    elif iBest == 3:
        model = RandomForestClassifier(max_depth=5, n_estimators=10)
    elif iBest == 4:
        model = MLPClassifier(alpha=0.05)
    else:
        model = AdaBoostClassifier()

    accuracies = []
    model.fit(X_train1k, y_1k)
    y_predict1k = model.predict(X_test1k)
    accuracies.append(accuracy(confusion_matrix(y_test, y_predict1k, label=[0, 1, 2, 3])))
        
    model.fit(X_train32k, y_train)
    y_predict32k = model.predict(X_test32k)
    accuracies.append(accuracy(confusion_matrix(y_test, y_predict32k, label=[0, 1, 2, 3])))

    csvResult.append(accuracies)

    with open("a1_3.3.csv", "w", newline="") as csvFile:
        csvWriter = csv.writer(csvFile)
        csvWriter.writerows(csvResult)



def class34( filename, i ):
    ''' This function performs experiment 3.4
    
    Parameters
       filename : string, the name of the npz file from Task 2
       i: int, the index of the supposed best classifier (from task 3.1)  
        '''
    # load data from file and turn y into list
    data = np.load(filename)    
    X = data[:,:-1]
    y = data[:,-1]
    # print(y)
    y = np.ravel(y)

    result = np.zeros((5,5))
    # all classifers
    allClassifiers = [LinearSVC(max_iter=10000),
        SVC(max_iter=10000, gamma=2),
        RandomForestClassifier(max_depth=5, n_estimators=10),
        MLPClassifier(alpha=0.05),
        AdaBoostClassifier()]

    data = KFold(n_splits=5, random_state=1, shuffle=True)
    k = 0
    # crossvalidation with 5 fold
    for train_index, test_index in kf.split(X):
        # get parameters
        # print("TRAIN:", train_index, "TEST:", test_index)
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]

        j = 0
        for model in allClassifiers:
            # get accuracy pre classifier
            model.fit(X_train, y_train)
            C = confusion_matrix(y_test, model.predict(X_test))
            result[k][j] = accuracy(C)
            j += 1
        k += 1

    # compare pvalues
    sList = []
    for a in range(5):
        if a != i-1:
            S = stats.ttest_rel(result[:,a], result[:, i-1])
            sList.append(S[1])

    with open("a1_3.4.csv", "w", newline="") as csvFile:
        csvWriter = csv.writer(csvFile)
        csvWriter.writerows(result)
        csvWriter.writerows(sList)
        csvWriter.writerows(["pvalue for best classifier from 3.1 is: " + S[0] 
                    + ""])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process each .')
    
    parser.add_argument("-i", "--input", help="the input npz file from Task 2", required=True)
    args = parser.parse_args()
    classBonus(args.input)
    # TODO : complete each classification experiment, in sequence.
    # X_train, X_test, y_train, y_test, iBest = class31(args.input)
    # X_1k, y_1k = class32(X_train, X_test, y_train, y_test,iBest)
    # class33(X_train, X_test, y_train, y_test, iBest, X_1k, y_1k)
    # class34(args.input, iBest)


