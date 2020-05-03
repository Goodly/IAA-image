import pandas as pd
import numpy as np
import re
import json
import os
from math import floor

data_hunt_path_OLD = "nyu_reconfig/NYU_Arguments-2020-02-24T0112-DataHunt.csv"
data_hunt_path = "COVID_new_format/Covid_Evidencev1-2020-04-02T1843-DataHunt.csv"
schema_path = "covid/Covid_Evidence2020_03_21-2020-03-24T0540-Schema.csv"

def testDataStorer():
    # explore(data_hunt_path)
    uberDict = dataStorer(data_hunt_path, schema_path)
    firstKey = list(uberDict.keys())[0]
    print(uberDict[firstKey])

def testQuestionLabelsList():
    data_hunt = pd.read_csv(data_hunt_path, encoding='utf-8')
    task_question_answer_labels = data_hunt.loc[:, ["quiz_task_uuid", "question_label", "answer_label"]
                                  ].drop_duplicates()
    first_task = task_question_answer_labels["quiz_task_uuid"][0]
    print(getQuestionLabels(task_question_answer_labels, first_task))

def testGetAnsAndAnsNum():
    data_hunt = pd.read_csv(data_hunt_path, encoding='utf-8')
    answer_id_text = data_hunt.loc[:,
                     ["quiz_task_uuid", "question_label", "answer_label", "answer_content", "answer_uuid",
                      "answer_text"]
                     ].drop_duplicates()
    task_question_answer_labels = data_hunt.loc[:, ["quiz_task_uuid", "question_label", "answer_label"]
                                  ].drop_duplicates()
    first_task = answer_id_text["quiz_task_uuid"][0]
    first_question = answer_id_text["question_label"][0]
    # print(getAns(answer_id_text, first_task, first_question))
    print(getAnsNumsList(task_question_answer_labels, first_task, first_question))

def testGetFromUberDict():
    data = dataStorer(data_hunt_path, schema_path)
    lastTask = list(data.keys())[-1]

    print(get_question_answers(data, lastTask, 1))
    print(get_question_userid(data, lastTask, 1))
    print(get_question_highlight_userid(data, lastTask, 1))
    print(get_question_start(data, lastTask, 1))
    print(get_question_end(data, lastTask, 1))
    print(get_question_numchoices(data, lastTask, 1))
    print(get_text_length(data, lastTask, 1))
    print(get_num_users(data, lastTask, 1))
    print(get_answer_texts(data, lastTask, 1))
    print(get_schema(data, lastTask))
    print(get_schema_sha256(data, lastTask))
    print(get_question_hlUsers(data, lastTask, 1))
    print(get_question_hlAns(data, lastTask, 1))
    print(get_article_num(data, lastTask))


def explore(data_hunt_path):
    data_hunt = pd.read_csv(data_hunt_path, encoding='utf-8')
    task_questions = data_hunt.loc[:, ["quiz_task_uuid", "question_label", "answer_label"]]
    print(task_questions[task_questions["quiz_task_uuid"] == task_questions["quiz_task_uuid"].loc[0]])


def dataStorer(data_hunt_path, schema_path):
    """
    Takes in a DataHunt csv file path and a Schema csv file path
    Returns a dictionary of all extracted information. See data structure on the onboarding document
    """
    data_hunt = pd.read_csv(data_hunt_path, encoding = 'utf-8')
    uberDict = {}

    # Creates multiple smaller tables for data access
    task_article = data_hunt.loc[:,["quiz_task_uuid", "article_batch_name", "article_number",
                                    "article_filename", "article_sha256", "article_text_length"
                                    ]].drop_duplicates().set_index("quiz_task_uuid")
    task_id_url_data = data_hunt.loc[:, ["quiz_task_uuid", "task_url", "tua_uuid"]].drop_duplicates()

    task_question_answer_labels = data_hunt.loc[:, [ "quiz_task_uuid", "question_label", "answer_label"]
                            ]

    taskrun_task = data_hunt.loc[:, ["quiz_task_uuid", "taskrun_count", "quiz_taskrun_uuid",
                                     "created", "finish_time", "elapsed_seconds", "contributor_uuid"]
               ].set_index("quiz_task_uuid")
    quest_label_text = data_hunt.loc[:, ["question_label", "question_text"]
                       ].drop_duplicates().set_index("question_label")
    answer_id_text = data_hunt.loc[:, ["quiz_task_uuid", "question_label", "answer_label", "answer_content", "answer_uuid", "answer_text"]
                     ].drop_duplicates()
    starts_ends = data_hunt.loc[:,["quiz_task_uuid", "question_label", "start_pos", "end_pos"]
                  ].set_index("quiz_task_uuid")
    highlight = data_hunt.loc[:, ["quiz_task_uuid", "question_label", "contributor_uuid",
                                  "target_text", "highlight_count", "answer_uuid", "answer_content", "answer_label", "answer_text"]
                ].set_index("quiz_task_uuid")
    highlighted_data = data_hunt.loc[:, ["quiz_task_uuid", "question_label", "contributor_uuid",
                                  "target_text", "highlight_count", "answer_uuid", "answer_content", "answer_label", "answer_text", "start_pos", "end_pos"]
                ]
    highlighted_data = highlighted_data[highlighted_data["highlight_count"] > 0]

    schemaData = pd.read_csv(schema_path, encoding = 'utf-8')



    # Finds schema name and sha
    schema_name = data_hunt["schema_namespace"].iloc[0]
    schema_sha = data_hunt["schema_sha256"].iloc[0]
    schema_topic = schemaData["topic_name"].iloc[0]

    # Creates a dictionary categorized by task_uuid
    for i in range(len(task_id_url_data)):
        record = task_id_url_data.iloc[i, :]
        uuid = record.loc["quiz_task_uuid"]
        url = record.loc["task_url"]
        tua_uuid = record.loc["tua_uuid"]
        article_record = task_article.loc[uuid, :]

        # Set up Schemma
        task_schema = schemaData[schemaData['schema_namespace'] == schema_name]
        dependencies = create_dependencies_dict(task_schema)
        schema_id = getSchemaSha(task_schema)


        # uberDict is indexed by uuid, which has two keys: taskData and quesData
        task = uberDict[uuid] = {}
        question_labels = getQuestionLabels(task_question_answer_labels, uuid)
        task['taskData'] = {
            "task_uuid": uuid,
            "task_url": url,
            "tua_uuid": tua_uuid,

            "article_name": article_record.loc["article_batch_name"],
            "article_num": article_record.loc["article_number"],
            "article_filename": article_record.loc["article_filename"],
            "article_sha": article_record.loc["article_sha256"],
            "length": article_record.loc["article_text_length"],

            "schema_name": schema_name,
            "schema_sha": schema_sha,
            "schema_id" : schema_id,
            "schema_topic" : schema_topic,
            'dependencies': dependencies,
            "question_labels": question_labels,
            "question_numbers" : getQuestionNumbersList(question_labels),


        }
        assert (schema_id == schema_sha)

        # computes the start and end lists
        starts_lists, ends_lists = getStartsEndsLists(starts_ends, uuid)

        # gets highlighted information
        usersGrouped = highlight.loc[uuid].groupby("question_label")
        contributors = usersGrouped["contributor_uuid"].apply(list)

        #
        # hasHighlightedTasks = False
        # if uuid in highlighted_data['quiz_task_uuid']:
        #     rel_hl_data = highlighted_data[highlighted_data['quiz_task_uuid'] == uuid]
        #     hl_users_data = rel_hl_data.groupby("question_label")["contributor_uuid"].apply(list)
        #     hl_ans_labels_data = rel_hl_data.groupby("question_label")["answer_label"].apply(list)
        #     hasHighlightedTasks = True

            # target_text = usersGrouped["target_text"].apply(list) # Don't know for sure
        answer_content = highlight.loc[uuid].groupby("question_label")["answer_content"].apply(list)
        newUsers = highlight.loc[uuid].groupby("question_label")["contributor_uuid"].unique().apply(list)
        rel_hl_data = highlighted_data[highlighted_data['quiz_task_uuid'] == uuid]
        # for each task, creates a new questionData that parses through related question and answer
        ques = uberDict[uuid]['quesData'] = {}
        for question_label in list(starts_lists.index):
            hightlightUsers = []
            hl_ans_nums = []
            target_text = []
            starts = []
            ends = []

            # print("Indices of highlight data under task", uuid, "are", rel_hl_data["question_label"])
            # print("The question label is: ", question_label)
            if rel_hl_data["question_label"].str.contains(question_label).any():
                # print("The indices are:", hl_users_data.index)
                question_hl_data = rel_hl_data[rel_hl_data["question_label"] == question_label]
                hightlightUsers = question_hl_data["contributor_uuid"].tolist()
                hl_ans_labels = question_hl_data["answer_label"].tolist()
                hl_ans_nums = [getAnsNumberFromLabel(l) for l in hl_ans_labels]
                target_text = question_hl_data["target_text"].tolist()
                starts =   question_hl_data['start_pos'].apply(floor).tolist()
                ends = question_hl_data['end_pos'].apply(floor).tolist()

                # print("Highlight Users are: ", hightlightUsers)
                # print("Highlight Answers are: ", hl_ans_labels)
                # print("Highlight target texts are: ", target_text)


            question_num = getQuestionNumberFromLabel(question_label)

            ques[question_num] = {
                    "answers" : getAnsNumsList(highlight, uuid, question_label), # list of answer numbers
                    "starts" : starts,
                    "ends" : ends,
                    "users" : getUsers(highlight, uuid, question_label),
                    "numUsers" : len(newUsers[question_label]),
                    "answer_content": find_answer_contents(task_schema, question_label),
                    "question_text": quest_label_text.loc[question_label, "question_text"],
                    "target_text": target_text, #TODO: currently returns a list of target texts, check!
                    "hlUsers": hightlightUsers,
                    'parents': dependencyStatus(dependencies, question_num),
                    "numChoices" : 10,
                    "hlAns": hl_ans_nums, # a list of highlighted answers
                }
    return uberDict


########### Helper Functions to Build the Dictionary. Output of DataStorer. ############

def getStartsEndsLists(starts_ends, uuid):
    """
    Gets the starts and ends DataFrame by uuid.
    Outputs a pair of DataFrames. Each entry is a LIST of start or end positions
    """
    grouped = starts_ends.loc[uuid].groupby("question_label")
    return grouped['start_pos'].apply(list), grouped['end_pos'].apply(list)

def getQuestionLabels(task_question_answer_labels, task_uuid):
    """
    Gets a list of question labels under the same task uuid
    """
    series = task_question_answer_labels[task_question_answer_labels["quiz_task_uuid"]  == task_uuid]
    return series["question_label"].unique().tolist()

def getAnsText(answer_id_text, task_uuid, question_label):
    """
    Returns a list of answers under the question label
    """
    task_data = answer_id_text[answer_id_text["quiz_task_uuid"] == task_uuid]
    ans = task_data[task_data["question_label"] == question_label].drop_duplicates(subset = ["contributor_uuid", "answer_uuid"])
    return ans["answer_text"].unique().tolist()

def getUsers(task_question_answer_labels, task_uuid, question_label):
    task_data = task_question_answer_labels.loc[task_uuid]
    ans = task_data[task_data["question_label"] == question_label].drop_duplicates(subset = ["contributor_uuid", "answer_uuid"])
    return ans["contributor_uuid"].tolist()

def getAnsLabels(task_question_answer_labels, task_uuid, question_label):
    task_data = task_question_answer_labels.loc[task_uuid]
    ans = task_data[task_data["question_label"] == question_label].drop_duplicates(subset = ["contributor_uuid", "answer_uuid"])
    return ans["answer_label"].tolist()

def getAnsNumsList(task_question_answer_labels, task_uuid, question_label):
    ans_labels = getAnsLabels(task_question_answer_labels, task_uuid, question_label)
    return [getAnsNumberFromLabel(l) for l in ans_labels]

def getAnsNumberFromLabel(label):
    return int(re.search(r'(?<=.A)\d+', label).group(0))

def getQuestionNumbersList(question_labels):
    return [getQuestionNumberFromLabel(label) for label in question_labels]

def getQuestionNumberFromLabel(label):
    return int(re.search(r'(?<=.Q)\d+', label).group(0))

def getSchemaTopic(schemaData):
    return schemaData.iloc[0]['topic_name']

def getSchemaSha(schemaData):
    return schemaData.iloc[0]['schema_sha256']

def getSchemaNamespace(ansData):
    return ansData['schema_namespace'].iloc[0]


########### Helper Functions to Check DEPENDENCIES and PARENTS  ############

def dependencyStatus(dependencies, qnum):
    try:
        return dependencies[qnum]
    except:
        return {}

def create_dependencies_dict(schemadata):
    """
    Creates a dictionary mapping from the parent question to all of its children
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
            indices, alpha, alphainc = getParentData(parents, parentdata)
    return parentdata, indices, alpha, alphainc

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

def getParentData(parents, parentData):
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

def get_indices_hard(string):

    if isinstance(string, list):
        if len(string == 1) and isinstance(string[0], str):
              string = string[0]
    out = []
    num = 0
    if not isinstance(string, str):
        return out
    for i in range(len(string)):
        if string[i].isdigit():
            num = 10*num+int(string[i])
        elif num!=0:
            out.append(num)
            num = 0

    return out

def find_answer_contents(schemadata, qlabel):
    questiondf = schemadata[schemadata['question_label'] == qlabel]
    pot_answers = questiondf['answer_content'].tolist()
    pot_answers.insert(0,'zero')
    return pot_answers


##################### GET the data from UberDict ##############

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
        return data[task_id]['taskData']['length'].iloc[0]
    except:
        return data[task_id]['taskData']['length']

def printType(iterable):
    for i in iterable:
        print(type(i))

def get_num_users(data, task_id, question_num):
    return data[task_id]['quesData'][question_num]['numUsers']

def get_answer_texts(data, task_id, question_num):
    return data[task_id]['quesData'][question_num]['target_text']

def get_schema(data, task_id):
    return data[task_id]['taskData']['schema_name']

def get_schema_sha256(data, task_id):
    return data[task_id]['taskData']['schema_sha']

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

def get_schema_topic(data, task_id):
    return data[task_id]['taskData']["schema_topic"]

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
def get_type_json(type, ques, config_path):
    with open(config_path+'/typing_dict.txt', 'r') as read_file:
        typing_dict = json.load(read_file)
    #typing_dict = json.loads(config_path+"/typing_dict.txt")

    out = typing_dict[type][str(ques)]
    return out[0], out[1]
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
                12: ['nominal', 5],
                13: ['ordinal', 10],
                14: ['ordinal', 10]
            },
        'Reasoning Specialist':
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
        'Quote Source Relevance':
            {
                1: ['nominal', 2],
                2: ['ordinal', 8],
                3: ['nominal', 2],
                4: ['checklist', 9],
                5: ['checklist', 9],
                6: ['checklist', 2],
                7: ['checklist', 6],
                8: ['ordinal', 7],
                9: ['ordinal', 10],
                10: ['ordinal', 10]
            },
        'Probability':
            {
                1:['ordinal', 3],
                2:['ordinal', 5],
                3:['ordinal', 3],
                4:['ordinal', 7],
                5:['ordinal', 3],
                6:['ordinal', 3],
                7:['ordinal', 5],
                8:['ordinal',10],
                9:['nominal', 1],
                10:['ordinal', 3],
                11:['ordinal', 4],
                12:['ordinal', 5],
                13:['ordinal', 10],
                14:['ordinal', 10]


            },
        'Holistic Evaluation of Article':
            {
                1: ['nominal', 9],
                2: ['nominal',1],
                3: ['checklist', 12],
                4: ['nominal',1],
                5: ['ordinal',5],
                6: ['checklist',8],
                7: ['ordinal', 5],
                8: ['ordinal', 5],
                9: ['checklist', 9],
                10: ['ordinal', 5],
                11: ['ordinal', 4],
                12: ['ordinal', 5],
                13: ['checklist', 5],
                14: ['nominal', 2],
                15: ['checklist', 3],
                16: ['nominal', 1],
                17: ['ordinal', 10],
                18: ['ordinal', 10]
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

###################### Helper Functions to Visualize a Dataframe #######################

def printColumnUniqueVals(data):
    for col in data.columns:
        print("{:30} {:>8}".format("Column: " + col, len(data[col].unique())))



