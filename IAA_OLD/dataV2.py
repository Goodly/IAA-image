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
        uberDict[task] = {
            'question_labels':qlabels,
            'question_numbers': qNums
        }

        #use Qlabels to find things in the input csvs, use Qnums within the program
        schema_name = get_schema(task_ans)
        task_schema = schemaData[schemaData['schema_namespace'] == schema_name]
        qDict = {}
        for i in range(len(qNums)):
            qnum = qNums[i]
            qlabel = findLabel(qlabels, qnum)
            print(qlabels, qNums)
            print('qnum',qnum)
            print('qlab', qlabel)
            numUsers = findNumUsers(task_schema, qlabel)
            q_type = get_q_type(task_schema, qlabel)
            print('qtype', q_type)
            #ANSWER block
            if q_type == 'CHECKBOX':
                answers, users= find_answers_checklist(task_ans, qnum)
            elif q_type == 'TEXT':
                answers, users = [0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            elif q_type == 'RADIO':
                answers, users = find_answers_radio(task_ans, qlabel, task_schema)
            starts, ends, hlUsers = findStartsEnds(task_schema, qlabel, task_hl)
            qDict[qnum] = {
               'answers': answers,
               'users': users,
               'numUsers': numUsers,
               'starts': starts,
               'ends': ends,
               'hlUsers': hlUsers
             }
        uberDict[task] = qDict
    print(uberDict)
    return uberDict

def findStartsEnds(schemadata, qlabel, highlightdata):
    questiondf = schemadata[schemadata['question_label'] == qlabel]
    hasHighlight = max(questiondf['nohighlight'])<1
    if hasHighlight:
        question_hl = highlightdata[highlightdata['question_label'] == qlabel]
        starts = question_hl['start_pos'].tolist()
        ends = question_hl['end_pos'].tolist()
        users = question_hl['contributor_uuid'].tolist()
        length = question_hl[]
        return starts, ends, users
    else:
        return [0], [0], [0]

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
    print("FINDING ANSWERS FOR CHCKLIST")
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
        users.append(users)
        print(ansCount)
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

def get_schema(ansData):
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

    return data[task_id][question_num]['answers']


def get_question_userid(data, task_id, question_num):
    return data[task_id][question_num]['users']

def get_question_highlight_userid(data, task_id, question_num):
    return data[task_id][question_num]['hlUsers']

def get_question_start(data, task_id, question_num):
    return data[task_id][question_num]['starts']

def get_question_end(data, task_id, question_num):
    return data[task_id][question_num]['ends']

def get_user_count(data, task_id, question_num):
    return data[task_id][question_num]['numUsers']


def get_user_count(article,question, csv_dict):
    return csv_dict[article][question][0]


def get_question_end(data, article_num, question_num):
    return data[article_num][question_num][1][3][0]

def get_text_length(data, article_num, question_num):
    return int(max(data[article_num][question_num][1][4][0]))
    #.iloc[0]

def get_num_users(data, article_num, question_num):
    return len(np.unique(get_question_userid(data, article_num, question_num)))

def get_question_type(data, article_num, question_num):
    return data[article_num][question_num][1][5][0].iloc[0]

def get_article_num(data, article):

    q  = min(data[article].keys())
    return data[article][q][1][6][0].iloc[0]


def get_namespace(data, article, question_num):
    return data[article][question_num][1][7][0].iloc[0]

def get_answer_texts(data, article_num, question_num):
    return data[article_num][question_num][1][8][0].tolist()

def get_question_text(data, article_num, question_num):
    return data[article_num][question_num][1][9][0].iloc[0]

def get_answer_content(data, article_num, question_num, answer_num):
    if answer_num == 'U' or answer_num == 'L' or answer_num == 'M' or answer_num == 'N/A':
        return answer_num

    answers = get_question_answers(data, article_num, question_num)
    index = finder(answers, answer_num)

    if index<0:
        return 'N/A'
    answer_contents = data[article_num][question_num][1][10][0]
    desired_content = answer_contents.tolist()[index]
    return desired_content

def finder(ser, a):
    if len(ser)<1:
        return -1
    for i in range(len(ser)):
            if ser[i]==a:
                    return i
    return -1
#############TEST CASES

ans = pd.read_csv('testans.csv')
print(ans.head(0))
q = ans['final_queue']


first = q.iloc[0]
tags = parseMany(first, separator = ',')
parseMany(first, 'Q', ',')
print(get_questions(ans))

data_storer('testhl.csv', 'testans.csv', 'testsch.csv')