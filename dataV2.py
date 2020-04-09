import pandas as pd
import numpy as np
import ast
from math import floor
import json
import os
from math import floor


def data_storer(path, answerspath, schemapath):
    """Function that turns csv data. Input the path name for the csv file.
    This will return a super dictionary that is used with other abstraction functions."""
    highlightData = pd.read_csv(path, encoding = 'utf-8')
    #below line added because now highlights csv also includes data from questions with no highlight attached to it
    highlightData = highlightData[highlightData["highlight_count"]!=0]
    answersData = pd.read_csv(answerspath, encoding = 'utf-8')
    schemaData = pd.read_csv(schemapath, encoding = 'utf-8')
    task_uuid = np.unique(answersData['quiz_task_uuid'])
    uberDict = {}
    for task in task_uuid:
        task_ans = answersData[answersData['quiz_task_uuid'] == task]
        task_hl = highlightData[highlightData['quiz_task_uuid'] == task]
        qlabels, qNums = get_questions(task_ans)
        uberDict[task] = {}


        #use Qlabels to find things in the input csvs, use Qnums within the program
        schema_name = find_schema(task_ans)
        task_schema = schemaData[schemaData['schema_namespace'] == schema_name]
        article_num, article_sha = find_article_data(task_ans)
        schema_style = find_schema_topic(task_schema)
        schema_id = find_schema_sha256(task_schema)
        tua_id = find_tua_uuid(task_hl)
        #down the road cache this to make it go faster
        dependencies = create_dependencies_dict(task_schema)
        uberDict[task]['taskData'] = {
            'question_labels': qlabels,
            'question_numbers': qNums,
            'article_num':article_num,
            'article_sha':article_sha,
            'schema_name':schema_style,
            'schema_id': schema_id,
            'dependencies': dependencies,
            'tua_uuid': tua_id
        }
        numUsersD = makeNumUsersDict(task_ans)
        qDict = {}
        for i in range(len(qNums)):
            qnum = qNums[i]
            qlabel = findLabel(qlabels, qnum)
            numUsers = findNumUsers(numUsersD, qlabel)
            q_type = get_q_type(task_schema, qlabel)
            answer_contents = find_answer_contents(task_schema, qlabel)
            question_text = find_question_text(task_schema, qlabel)
            #ANSWER block
            if q_type == 'CHECKBOX':
                answers, users= find_answers_checklist(task_ans, qnum)
            elif q_type == 'TEXT':
                answers, users = [0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0]
            elif q_type == 'RADIO':
                answers, users = find_answers_radio(task_ans, qlabel, task_schema)
                assert(len(answers) == len(users))
            starts, ends, hlUsers, length, targetText, hlAns = findStartsEnds(task_schema, qlabel, task_hl)
            qDict[qnum] = {
               'answers': answers,
                'numChoices':10,
               'users': users,
               'numUsers': numUsers,
               'starts': starts,
               'ends': ends,
               'hlUsers': hlUsers,
               'length': length,
               'target_text': targetText,
                'hlAns': hlAns,
                'answer_content': answer_contents,
                'question_text': question_text,
                'parents': dependencyStatus(dependencies, qnum)
             }
        uberDict[task]['quesData'] = qDict
    return uberDict


def dependencyStatus(dependencies, qnum):
    try:
        return dependencies[qnum]
    except:
        return {}
def evalDependency(data, task_id, parentdata, question, answer, indices, alpha, alphainc):
    depDict = get_article_dependencies(data, task_id)
    try:
        l = answer+5
        isInt = True
    except:
        isInt = False
    if isInt and isinstance(indices, list):
        parentdata = saveParentData(depDict, parentdata,question, answer, indices, alpha, alphainc)
    elif isinstance(answer, int):
        if checkIfChild(depDict, question):
            parents = get_question_parents(data, task_id, question)
            indices, alpha, alphainc = get_parent_data(parents, parentdata)
    return parentdata, indices, alpha, alphainc

def get_parent_data(parents, parentData):
    indices = []
    alpha = []
    alphainc = []
    for p in parents.keys():
        for a in parents[p]:
            try:
                newInd = parentData[p][a][0]
                newAlph = parentData[p][a][1]
                newAlphinc = parentData[p][a][2]
                indices.append(newInd)
                alpha.append(newAlph)
                newAlphinc.append(newAlphinc)
            except:
                print('parentdata not found')
    indices = np.unique(indices)
    alpha = average(alpha)
    alphainc = average(alphainc)
    return indices, alpha, alphainc


def average(alpha):
    if len(alpha) == 0:
        return 0
    return np.mean(alpha)
def checkIfChild(depDict, question):
    if question in depDict.keys():
        return True
def saveParentData(dependenciesDict, parentData, question, answer, indices, alpha, alphainc):
    if checkIfParent(dependenciesDict, question, answer):
        parentData[question] = parentAddendum(parentData, answer, [indices, alpha, alphainc])
    return parentData
def parentAddendum(parentData, answer, newStuff):
    if answer not in parentData.keys():
        parentData[answer] = [newStuff]
    else:
        parentData[answer].append(newStuff)
    return parentData
def checkIfParent(dependenciesDict, question, answer):
    for k in dependenciesDict.keys():
        if question in dependenciesDict[k].keys():
            if answer in dependenciesDict[k][question]:
                return True
            return False


def create_dependencies_dict(schemadata):
    """

    creates a dictionary mapping from the parent question to all of its children
    """
    dependers = schemadata[schemadata['answer_next_questions'].notnull()]
    allChildren = dependers['answer_next_questions'].tolist()
    parents = dependers['answer_label'].tolist()
    tempDict = dict()
    for i in range(len(allChildren)):
        dictAddendumList(tempDict, allChildren[i], parents[i])
    d = {}
    for k in tempDict.keys():
        questions = parseMany(k,'Q',',')
        thisParents = tempDict[k]
        thisParentQs = [parse(thisParent, 'Q', '.') for thisParent in thisParents]
        thisParentAs = [parse(thisParent, 'A', ',') for thisParent in thisParents]
        extendedFamDict = {}
        for i in range(len(thisParentQs)):
            extendedFamDict = dictAddendumList(extendedFamDict, thisParentQs[i], thisParentAs[i])
        for q in questions:
            #d[q] = extendedFamDict
            d = dictAddendumDict(d, q, extendedFamDict)

    # parQuestions = [parse(parLab, 'Q', '.') for parLab in parents]
    # parAnswers = [parse(parLab, 'A', '.') for parLab in parents]
    # childQuestions = [parse(childLabel, 'Q', ',') for childLabel in allChildren]
    return d
def dictAddendumDict(dict, key, newDict):
    if key not in dict.keys():
        dict[key] = newDict
    else:
        for k in newDict:
            if k in dict[key].keys():
                dict[key][k].append(newDict[k][0])
            else:
                dict[key][k] = newDict[k][0]
    return dict

def dictAddendumList(dict, key, newFriend):
    if key not in dict.keys():
        if isinstance(newFriend, list):
            dict[key] = newFriend
        else:
            dict[key] = [newFriend]
    else:
        curr = dict[key]
        curr.append(newFriend)
    return dict
def find_question_text(schemadata,qlabel):
    questiondf = schemadata[schemadata['question_label'] == qlabel]
    qText = questiondf['question_text'].iloc[0]
    return qText


def find_answer_contents(schemadata, qlabel):
    questiondf = schemadata[schemadata['question_label'] == qlabel]
    pot_answers = questiondf['answer_content'].tolist()
    pot_answers.insert(0,'zero')
    return pot_answers


def find_article_data(task_ans):
    return task_ans['article_number'].iloc[0], task_ans['article_sha256'].iloc[0]




def indicesFromString(indices):
    indices = clearBogusChars(indices)
    try:
        return json.loads(indices)
    except TypeError:
        return json.loads((str(indices).replace(' ', ', ')))
    except:
        filtered = []
        for s in indices:
            f = s.replace('\n', '')
            if ',' not in f:
                f = f.replace(' ', ', ')
            f = ast.literal_eval(f)
            filtered.append(f)
    return filtered
def clearBogusChars(string):
    if not isinstance(string, str):
        string = str(string)
    string = string.replace("\\", "")
    string = string.replace("\n", '')
    string = string.replace('n', '')
    string = string.replace("'", '')
    string = string.replace('"', '')
    string = string.replace(' , ', '')
    string = string.strip()
    string = string.replace(',,',',')
    i = 1
    while not string[i].isdigit():
        i+=1
    string = string[0]+string[i:]
    return string
def findStartsEnds(schemadata, qlabel, highlightdata):
    # hasHighlight = max(questiondf['nohighlight'])<1
    # if hasHighlight:
    #TODO: implement a check to see if people thought there should've been a highlight
    #Don't filter by answer for checklist questions here
    relevant_hl = highlightdata[highlightdata['question_label'] == qlabel]
    starts = relevant_hl['start_pos'].apply(floor).tolist()
    ends = relevant_hl['end_pos'].apply(floor).tolist()
    users = relevant_hl['contributor_uuid'].tolist()
    length = relevant_hl['article_text_length']
    answerText = relevant_hl['target_text'].str.decode('unicode-escape')
    answer_labels = relevant_hl['answer_label']
    answer_nums = [parse(ans, 'A') for ans in answer_labels]
    return starts, ends, users, length, answerText, answer_nums
    #else:
        #return [0], [0], [0], 0, '',[0]


def checkIfHighlight(answers, qlabel, questiondf):
    numAns = len(answers)
    ansLabels = [AnstoLabel(ans) for ans in answers]


def AnstoLabel(answer, qlabel):
    return qlabel+'.A'+str(answer)
def makeNumUsersDict(answerData):
    queue = answerData['final_queue']
    d = {}
    for ro in queue:
        lis = parseMany(ro, separator=',')
        for label in lis:
            d = dictIncrement(d, label)
    return d
def dictIncrement(dict, k):
    if not k in dict.keys():
        dict[k] = 1
    else:
        dict[k] = dict[k]+1
    return dict
def findNumUsers(numUsersDict, qlabel):
    """

    :param schemadata: df from current schema
    :param qlabel: questionlabel of current question
    :return: numUsers,
    """
    return numUsersDict[qlabel]


def find_answers_radio(ansData, qlabel, schemaData):
    ansData = ansData.dropna(subset=[qlabel])
    col = ansData[qlabel]
    assert (len(col) == len(col.dropna()))
    stringAnswers = col.tolist()
    users = ansData['contributor_uuid'].tolist()
    assert(len(stringAnswers) == len(users))
    numAnswers = []
    for ans in stringAnswers:
        if isinstance(ans, int):
            numAnswers.append(ans)
        else:
            numAnswers.append(stringAnsToInt(schemaData, ans, qlabel))
    return numAnswers, users


def stringAnsToInt(schemadata, answer, qlabel):
    questiondf = schemadata[schemadata['question_label'] == qlabel]
    ansMatched = questiondf[questiondf['answer_content'] == answer]
    ansLabel = ansMatched['answer_label'].iloc[0]
    numAnswer = parse(ansLabel,'A')
    return numAnswer
def findLabel(qlabels, qnum):
    for label in qlabels:
        if str(qnum) in label:
            if parse(label, 'Q') == qnum:
                return label

def find_answers_checklist(ans_data, qnum):
    columns = ans_data.head(0)
    good_cols =find_matching_columns(columns, qnum)
    answers = []
    users = []
    for colName in good_cols:
        aNum = parse(colName, 'A')
        column = ans_data[colName]
        ansCount = sum(column)
        answeredRows = ans_data[ans_data[colName]!=0]
        newUsers = answeredRows['contributor_uuid'].tolist()
        for newU in range(len(newUsers)):
            users.append(newUsers[newU])

        for i in range(ansCount):
            answers.append(aNum)
    return answers, users
def find_matching_columns(cols, qnum):
    #This needs columns to be in ascending order by question number
    out = []
    found = False
    answerCols = []
    for col in cols:
        if 'Q' in col and '.' in col:
            if parse(col, 'Q', '.') == qnum:
                out.append(col)
    return np.unique(out)


def get_q_type(schemaData, qLabel):

    return schemaData[schemaData['question_label'] == qLabel].iloc[0]['question_type']
def get_indices_hard(string):

    if isinstance(string, list):
        if len(string == 1) and isinstance(string[0], str):
              string = string[0]
    out = []
    num = 0
    for i in range(len(string)):
        if string[i].isdigit():
            num = 10*num+int(string[i])
        elif num!=0:
            out.append(num)
            num = 0

    return out

def find_schema_topic(schemaData):

    return schemaData.iloc[0]['topic_name']
def find_schema_sha256(schemaData):

    return schemaData.iloc[0]['schema_sha256']
def find_schema(ansData):

    return ansData['schema_namespace'].iloc[0]

def find_tua_uuid(hlData):
    try:
        return hlData['tua_uuid'].iloc[0]
    except IndexError:
        print("BUG: NO TUA FOIUND")
        return 0


def get_questions(ansData):
    relTags = np.zeros(0)
    relNums = np.zeros(0)
    for queue in ansData['final_queue']:
        relTags = np.append(relTags, parseMany(queue, separator = ','))
        #qnum = parseMany(queue, field = 'Q', separator = ',')
        #tnum =
        relNums = np.append(relNums, parseMany(queue, field = 'Q', separator=','))
    relTags = np.unique(relTags)
    relNums = np.unique(relNums).astype(int)
    return relTags, relNums

def readIndices(strIndices):
    #end = strIndices.index(']')
    separated = parseMany(strIndices[1:-1], separator = ' ')
    fin = [int(floor(float(i))) for i in separated]
    return fin

def parseMany(base, field = None, separator = None):
    """
    returns
    :param base: input string
    :param field: char that you want the number after
    :param separator: char separating useful strings
    :return: the field desired, if there's a separator returns a list of everything from the field
    """
    if separator == None:
        return parse(base, field)
    else:
        out = []
        while len(base)>0:
            if separator in base:
                end = base.index(separator)
            else:
                end = len(base)
            label = parse(base[:end], field)
            out.append(label)
            base = base[end+1:]
    return out

def parse(base, field, end = None):
    if field == None:
        return base.strip()
    if end != None:
        aSpot = base.index(field)
        rest  =base[aSpot:]
        try:
            eSpot = rest.index(end)+aSpot
        except:
            return int(base[aSpot+1:])
        #if this is a bug then has to be end+1 or end -1
        ansString = base[aSpot +1: eSpot]
        return int(ansString)
    aSpot = base.index(field)
    ansString = base[aSpot+1:]
    return int(ansString)

def get_question_answers(data, task_id, question_num):

    return data[task_id]['quesData'][question_num]['answers']


def get_question_userid(data, task_id, question_num):
    return data[task_id]['quesData'][question_num]['users']

def get_question_highlight_userid(data, task_id, question_num):
    return data[task_id]['quesData'][question_num]['hlUsers']

def get_question_start(data, task_id, question_num):
    return data[task_id]['quesData'][question_num]['starts']

def get_question_end(data, task_id, question_num):
    return data[task_id]['quesData'][question_num]['ends']

def get_question_numchoices(data, task_id, question_num):
    return data[task_id]['quesData'][question_num]['numChoices']

def get_text_length(data, task_id, question_num):
    try:
        #TODO investigate why this is sometimes a series
        return data[task_id]['quesData'][question_num]['length'].iloc[0]
    except:
        return data[task_id]['quesData'][question_num]['length']

def printType(iterable):
    for i in iterable:
        print(type(i))
def get_num_users(data, task_id, question_num):
    return data[task_id]['quesData'][question_num]['numUsers']

def get_answer_texts(data, task_id, question_num):
    return data[task_id]['quesData'][question_num]['target_text'].tolist()

def get_schema(data, task_id):
    return data[task_id]['taskData']['schema_name']

def get_schema_sha256(data, task_id):
    return data[task_id]['taskData']['schema_id']

def get_question_hlUsers(data, task_id, question_num):
    return data[task_id]['quesData'][question_num]['hlUsers']
def get_question_hlAns(data, task_id, question_num):
    return data[task_id]['quesData'][question_num]['hlAns']

def get_article_num(data,task_id):
    return data[task_id]['taskData']['article_num']

def get_tua_uuid(data,task_id):
    return data[task_id]['taskData']['tua_uuid']

def get_article_sha(data,task_id):
    return data[task_id]['taskData']['article_sha']


def get_question_type(data, task_id, question_num):
    return None


def get_answer_content(data, task_id, question_num, answer_num):
    if answer_num == 'U' or answer_num == 'L' or answer_num == 'M' or answer_num == 'N/A':
        return answer_num
    contents = data[task_id]['quesData'][question_num]['answer_content']
    myAnswer = contents[answer_num]
    return myAnswer

def get_question_text(data, task_id, question_num):
    return data[task_id]['quesData'][question_num]['question_text']

def get_question_parents(data, task_id, question_num):
    return data[task_id]['quesData'][question_num]['parents']

def get_article_dependencies(data,task_id):
    return data[task_id]['taskData']['dependencies']

def get_namespace(data, article, question_num):
    return data[article][question_num][1][7][0].iloc[0]

def finder(ser, a):
    if len(ser)<1:
        return -1
    for i in range(len(ser)):
            if ser[i]==a:
                    return i
    return -1

def make_directory(directory):
    print(directory)
    if directory[-1] != '/':
        directory = directory +'/'
    try:
        os.mkdir(directory)
    except FileExistsError:
        pass
    return directory

def get_type_hard(type, ques):
    #ques = parse(ques, 'Q')
    #print('type', type, ques)
    typing_dict = {
        'Source relevance':
            {
                1: ['checklist', 9],
                2: ['nominal', 2],
                3: ['ordinal', 6],
                4: ['ordinal', 8]
            },
        #OLD
        'Science and Causality Questions for SSS Students V2':
            {
                5:['nominal', 1],
                6: ['checklist', 8],
                9:['ordinal', 4],
                10:['nominal', 1]
            },
        #OLD
        'Language Specialist V2':
            {
                1:['checklist',9],
                6:['checklist', 8],

            },
        'Language Specialist V3':
            {
                1:['checklist', 13],
                2:['ordinal', 5],
                3:['ordinal', 5],
                4:['ordinal', 6],
                5:['checklist', 8],
                6:['nominal', 1],
                7:['ordinal',5],
                8:['ordinal', 5],
                9:['ordinal', 5],
                10: ['ordinal', 5],
                11: ['ordinal', 4],
                12: ['ordinal', 10],
                13: ['ordinal', 10],
                15: ['ordinal', 10]
            },
        'Language Specialist V4':
            {
                1:['checklist', 13],
                2:['ordinal', 5],
                3:['ordinal',5],
                5:['ordinal', 5],
                6:['ordinal', 8],
                7:['nominal', 1],
                9:['ordinal', 5],
                10:['ordinal',4],
                11:['ordinal',5],
                12:['ordinal', 4],
                13:['ordinal', 5],
                14:['ordinal', 10],
                15:['ordinal', 10]

            },
        'Confidence':
            {
                1:['ordinal', 3],
                2:['ordinal', 5],
                4:['ordinal', 3],
                5:['ordinal', 3],
                6:['nominal', 5],
                7:['ordinal', 3],
                8:['ordinal', 5],
                9:['ordinal', 5],
                10:['ordinal', 3],
                11:['ordinal', 4],
                12:['checklist', 4],
                13:['ordinal', 10],
                14:['ordinal', 10]
            },
        'Probability Specialist':
            {
                1: ['ordinal', 3],
                2: ['ordinal', 5],
                4: ['ordinal', 3],
                5: ['ordinal', 3],
                6: ['nominal', 5],
                7: ['nominal', 5],
                8: ['ordinal', 5],
                9: ['ordinal', 5],
                10: ['ordinal', 3],
                11: ['ordinal', 4],
                12: ['nominal', 4],
                13: ['ordinal', 10],
                14: ['ordinal', 10]
            },
        'Reasoning Specialist V4':
            {
                1: ['checklist', 6],
                2:['checklist', 6],
                3: ['checklist', 7],
                4: ['ordinal', 3],
                5: ['ordinal', 3],
                6: ['checklist', 10],
                7: ['ordinal', 5],
                8: ['nominal', 1],
                9: ['ordinal', 10],
                10: ['ordinal', 10]
            },
        'Probability Specialist V4':
            {
                1: ['ordinal', 3],
                2: ['ordinal', 5],
                5: ['ordinal', 3],
                6: ['ordinal', 3],
                7: ['ordinal', 5],
                10: ['ordinal', 3],
                11: ['ordinal', 4],
                12: ['ordinal', 5],
                13: ['ordinal', 10],
                14: ['ordinal', 10]
            },
        'Evidence Specialist':
            {
                1:['checklist', 3],
                2:['checklist', 9],
                #TODO: this is an interval quesiton, prob gonna get ignored l8r though
                3:['nominal', 1],
                4:['ordinal', 6],
                5:['ordinal', 5],
                6:['nominal', 3],
                7:['nominal', 1],
                8:['ordinal', 5],
                9:['ordinal', 3],
                10:['ordinal', 5],
                11:['ordinal', 5],
                12:['ordinal', 4],
                13:['ordinal', 10],
                14:['ordinal', 10]
            },
        'Evidence Specialist 3':
            {
                1: ['checklist', 3],
                2: ['checklist', 9],
                # TODO: this is an interval quesiton, prob gonna get ignored l8r though
                3: ['nominal', 1],
                4: ['ordinal', 5],
                5: ['ordinal', 6],
                6: ['ordinal', 6],
                7: ['nominal', 3],
                8: ['nominal', 1],
                9: ['ordinal', 7],
                10: ['ordinal', 3],
                11: ['ordinal', 5],
                12: ['ordinal', 5],
                13: ['ordinal', 4],
                14: ['ordinal', 10],
                15: ['nominal', 1]
            },
        'Beginner Reasoning Specialist Structured':
            {
                1:['checklist', 5],
                2:['checklist', 6],
                3:['checklist', 7],
                4:['ordinal', 3],
                5:['ordinal', 3],
                6:['checklist', 9],
                7:['ordinal', 6],
                8:['nominal', 1],
                #hardness
                9:['ordinal', 10],
                #confidence
                10:['ordinal', 10]
            },
        'Evidence':
            {
                5:['ordinal', 3],
                6:['checklist', 7],
                12:['nominal', 1]

            },
        'Argument relevance':
            {
                1:['ordinal', 6],
                2: ['ordinal', 10],
                3: ['ordinal', 10]
            },
        'Source relevance':
            {
                1:['checklist', 9],
                2:['checklist', 2],
                3:['checklist', 6],
                4:['ordinal', 8],
                5:['ordinal', 10],
                6:['ordinal', 10]
            },
        'Probability':
            {
                1:['ordinal', 3],
                2:['ordinal', 5],
                3:['ordinal', 3],
                4:['ordinal', 7],
                5:['ordinal', 3],
                6:['ordinal', 4],
                7:['ordinal', 5],
                8:['ordinal',10],
                9:['nominal', 1]
            },
        'Holistic Evaluation of Article':
            {
                1:['ordinal', 5],
                2:['ordinal',5],
                3: ['checklist', 11],
                4: ['checklist',5],
                5: ['nominal',1],
                6:['ordinal',5],
                7:['ordinal', 5]
            }

    }

    out = typing_dict[type][ques]
    #print('typing success', out[0], out[1])
    return out[0], out[1]


#for purpose of naming outputFile
def get_path(fileName):
    name = ''
    path = ''
    for c in fileName:
        name = name +c
        if c == '/':
            path = path + name
            name = ''
    return path, name

#############TEST CASES

# ans = pd.read_csv('testans.csv')
# print(ans.head(0))
# q = ans['final_queue']
#
#
# first = q.iloc[0]
# tags = parseMany(first, separator = ',')
# parseMany(first, 'Q', ',')
# print(get_questions(ans))

#data_storer('testhl.csv', 'testans.csv', 'testsch.csv')