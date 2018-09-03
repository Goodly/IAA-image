import pandas as pd
import numpy as np

def data_storer(path, answerspath, schemapath):
    """Function that turns csv data. Input the path name for the csv file.
    This will return a super dictionary that is used with other abstraction functions."""
    highlightData = pd.read_csv(path, encoding = 'utf-8')
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
        #down the road cache this to make it go faster
        dependencies = create_dependencies_dict(task_schema)
        uberDict[task]['taskData'] = {
            'question_labels': qlabels,
            'question_numbers': qNums,
            'article_num':article_num,
            'article_sha':article_sha,
            'schema_name':schema_style,
            'dependencies': dependencies
        }
        print('dependencies dict', dependencies)
        qDict = {}
        for i in range(len(qNums)):
            qnum = qNums[i]
            qlabel = findLabel(qlabels, qnum)
            #print(qlabels, qNums)
            #print('qnum',qnum)
            #print('qlab', qlabel)
            numUsers = findNumUsers(task_schema, qlabel)
            q_type = get_q_type(task_schema, qlabel)
            answer_contents = find_answer_contents(task_schema, qlabel)
            question_text = find_question_text(task_schema, qlabel)
            #print('qtype', q_type)
            #ANSWER block
            if q_type == 'CHECKBOX':
                answers, users= find_answers_checklist(task_ans, qnum)
            elif q_type == 'TEXT':
                answers, users = [0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            elif q_type == 'RADIO':
                answers, users = find_answers_radio(task_ans, qlabel, task_schema)
            starts, ends, hlUsers, length, targetText, hlAns = findStartsEnds(task_schema, qlabel, task_hl)
            print('THESESHOULDBESAME', len(starts), len(ends), len(hlUsers))
            qDict[qnum] = {
               'answers': answers,
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
    #print(uberDict)
    return uberDict
def dependencyStatus(dependencies, qnum):
    try:
        print('theseareparents',dependencies[qnum])
        return dependencies[qnum]
    except:
        return {}
def evalDependency(data, task_id, parentdata, question, answer, indices, alpha, alphainc):
    print(len(indices))
    depDict = get_article_dependencies(data, task_id)
    print('dep Here')
    print(depDict)
    print(isinstance(answer, int))
    print(isinstance(indices, list))
    try:
        l = answer+5
        isInt = True
    except:
        isInt = False
    print(answer, indices,(isinstance(indices, list)) )
    print("ISNTITFUN", isInt)
    if isInt and isinstance(indices, list):
        print('savingPrents')
        parentdata = saveParentData(depDict, parentdata,question, answer, indices, alpha, alphainc)
    elif isinstance(answer, int):
        if checkIfChild(depDict, question):
            parents = get_question_parents(data, task_id, question)
            print("PARENTSLOVEYOU", parents)
            indices, alpha, alphainc = get_parent_data(parents, parentdata)
    return parentdata, indices, alpha, alphainc

def get_parent_data(parents, parentData):
    indices = []
    alpha = []
    alphainc = []
    print('parreents', parents)
    print("PDAT", parentData)
    for p in parents.keys():
        for a in parents[p]:
            try:
                print('h1')
                newInd = parentData[p][a][0]
                newAlph = parentData[p][a][1]
                newAlphinc = parentData[p][a][2]
                print('h2')
                indices.append(newInd)
                alpha.append(newAlph)
                newAlphinc.append(newAlphinc)
                print('got parent data')
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
    print(parentData)
    print(answer)
    print('thoiswereinpts')
    if answer not in parentData.keys():
        parentData[answer] = [newStuff]
    else:
        parentData[answer].append(newStuff)
    return parentData
def checkIfParent(dependenciesDict, question, answer):
    for k in dependenciesDict.keys():
        print('a key exists')
        if question in dependenciesDict[k].keys():
            print('inthefirst')
            print(dependenciesDict[k])
            if answer in dependenciesDict[k][question]:
                print('gotparent')
                return True
            print('notparent')
            return False


def create_dependencies_dict(schemadata):
    dependers = schemadata[schemadata['answer_next_questions'].notnull()]
    print(dependers)
    allChildren = dependers['answer_next_questions'].tolist()
    print('children', allChildren)
    parents = dependers['answer_label'].tolist()
    tempDict = dict()
    for i in range(len(allChildren)):
        dictAddendumList(tempDict, allChildren[i], parents[i])
    print('THIS DICT', tempDict)
    d = {}
    for k in tempDict.keys():
        questions = parseMany(k,'Q',',')
        print('questions', questions)
        thisParents = tempDict[k]
        print('padres', thisParents)
        thisParentQs = [parse(thisParent, 'Q', '.') for thisParent in thisParents]
        thisParentAs = [parse(thisParent, 'A', ',') for thisParent in thisParents]
        print('qs', thisParentQs)
        print(thisParentAs)
        extendedFamDict = {}
        for i in range(len(thisParentQs)):
            extendedFamDict = dictAddendumList(extendedFamDict, thisParentQs[i], thisParentAs[i])
        print('efd', extendedFamDict)
        for q in questions:
            #d[q] = extendedFamDict
            d = dictAddendumDict(d, q, extendedFamDict)
        print('d',d)
    print(len(allChildren), len(parents))
    print('theOne', d)
    # parQuestions = [parse(parLab, 'Q', '.') for parLab in parents]
    # parAnswers = [parse(parLab, 'A', '.') for parLab in parents]
    # childQuestions = [parse(childLabel, 'Q', ',') for childLabel in allChildren]
    return d
def dictAddendumDict(dict, key, newDict):
    if key not in dict.keys():
        dict[key] = newDict
    else:
        for k in newDict:
            print(dict)
            print(dict[key])
            if k in dict[key].keys():
                dict[key][k].append(newDict[k][0])
            else:
                dict[key][k] = newDict[k][0]
    return dict

def deepAddendumDicts(dict, key,newDict):
    return
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
    print(pot_answers)
    return pot_answers
def find_article_data(task_ans):
    return task_ans['article_number'].iloc[0], task_ans['article_sha256'].iloc[0]
def findStartsEnds(schemadata, qlabel, highlightdata):
    questiondf = schemadata[schemadata['question_label'] == qlabel]
    hasHighlight = max(questiondf['nohighlight'])<1
    if hasHighlight:
        question_hl = highlightdata[highlightdata['question_label'] == qlabel]
        starts = question_hl['start_pos'].tolist()
        ends = question_hl['end_pos'].tolist()
        users = question_hl['contributor_uuid'].tolist()
        length = question_hl['source_text_length']
        answerText = question_hl['target_text']
        answer_labels = question_hl['answer_label']
        answer_nums = [parse(ans, 'A') for ans in answer_labels]
        return starts, ends, users, length, answerText, answer_nums
    else:
        return [0], [0], [0], 0, '',[0]

def findNumUsers(schemadata, qlabel):
    """

    :param schemadata: df from current schema
    :param qlabel: questionlabel of current question
    :return: numUsers,
    """
    questiondf = schemadata[schemadata['question_label'] == qlabel]
    numUsers = questiondf['answer_count'].iloc[0]
    return numUsers


def find_answers_radio(ansData, qlabel, schemaData):
    col = ansData[qlabel]
    stringAnswers = col.dropna().tolist()
    users = ansData['contributor_uuid'].tolist()
    for u in users:
        print(type(u))
    #print(ansData['contributor_uuid'].tolist())
    numAnswers = []
    for ans in stringAnswers:
        numAnswers.append(stringAnsToInt(schemaData, ans, qlabel))
    return numAnswers, users


def stringAnsToInt(schemadata, answer, qlabel):
    questiondf = schemadata[schemadata['question_label'] == qlabel]
    ansMatched = questiondf[questiondf['answer_content'] == answer]
    ansLabel = ansMatched['answer_label'].iloc[0]
    numAnswer = parse(ansLabel,'A')
    return numAnswer
def findLabel(qlabels, qnum):
    #print('finding', qnum)
    for label in qlabels:
        #print(label)
        if str(qnum) in label:
            #print('step1')
            #print(label)
            if parse(label, 'Q') == qnum:
                return label

def find_answers_checklist(ans_data, qnum):
    #print("FINDING ANSWERS FOR CHCKLIST")
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
            print(newUsers[newU])
            users.append(newUsers[newU])

        #print(ansCount)
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


def find_schema_topic(schemaData):

    return schemaData.iloc[0]['topic_name']

def find_schema(ansData):

    return ansData['schema_namespace'].iloc[0]

def get_questions(ansData):
    relTags = np.zeros(0)
    relNums = np.zeros(0)
    for queue in ansData['final_queue']:
        relTags = np.append(relTags, parseMany(queue, separator = ','))
        relNums = np.append(relNums, parseMany(queue, field = 'Q', separator=','))
    relTags = np.unique(relTags)
    relNums = np.unique(relNums).astype(int)
    return relTags, relNums

def readIndices(strIndices):
    print(strIndices)
    #end = strIndices.index(']')
    separated = parseMany(strIndices[1:-1], separator = ' ')
    fin = [int(i) for i in separated]
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
    #print('BAASSEE', base)
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


def get_text_length(data, task_id, question_num):
    try:
        #TODO investigate why this is sometimes a series
        return data[task_id]['quesData'][question_num]['length'].iloc[0]
    except:
        return data[task_id]['quesData'][question_num]['length']


def get_num_users(data, task_id, question_num):
    print("6666 this got caled")
    return data[task_id]['quesData'][question_num]['numUsers']

def get_answer_texts(data, task_id, question_num):
    return data[task_id]['quesData'][question_num]['target_text'].tolist()

def get_schema(data, task_id):
    return data[task_id]['taskData']['schema_name']

def get_question_hlUsers(data, task_id, question_num):
    return data[task_id]['quesData'][question_num]['hlUsers']
def get_question_hlAns(data, task_id, question_num):
    return data[task_id]['quesData'][question_num]['hlAns']

def get_article_num(data,task_id):
    return data[task_id]['taskData']['article_num']
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
    print(data[task_id])
    return data[task_id]['quesData'][question_num]['parents']

def get_article_dependencies(data,task_id):
    print('dependenciesgoingout')
    print(data[task_id]['taskData']['dependencies'])
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

def get_type_hard(type, ques):
    #ques = parse(ques, 'Q')
    #print('type', type, ques)
    #TODO:verify all of this against the schema
    typing_dict = {
        'Source relevance':
            {
                1: ['checklist', 7],
                2: ['checklist', 8],
                3: ['ordinal', 5]
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
                5:['ordinal', 5],
                6:['nominal', 8],
                7:['nominal',1],
                #TODO: is this ordinal?
                8:['ordinal', 4],
                9:['ordinal', 5],
                10: ['ordinal', 4],
                11: ['ordinal', 5],
                12: ['ordinal', 3],
                13: ['ordinal', 5],
                15: ['ordinal', 10],
                14: ['ordinal', 10]
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
        'Evidence Specialist':
            {
                2:['checklist', 3],
                3:['checklist', 9],
                #TODO: this is an interval quesiton, prob gonna get ignored l8r though
                4:['nominal', 1],
                5:['ordinal', 6],
                6:['ordinal', 5],
                7:['nominal', 3],
                8:['nominal', 1],
                9:['ordinal', 5],
                11:['ordinal', 3],
                12:['ordinal', 5],
                13:['ordinal', 5],
                14:['ordinal', 4],
                15:['ordinal', 10],
                16:['ordinal', 10]
            },
        'Beginner Reasoning Specialist Structured':
            {
                1:['checklist', 5],
                2:['checklist', 6],
                3:['checklist', 7],
                4:['ordinal', 3],
                5:['ordinal', 3],
                6:['checklist', 8],
                7:['ordinal', 5],
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
                1:['ordinal', 6]
            },
        'Source relevance':
            {
                1:['checklist', 9],
                2:['checklist', 2],
                3:['checklist', 5],
                4:['ordinal', 7]
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

data_storer('testhl.csv', 'testans.csv', 'testsch.csv')