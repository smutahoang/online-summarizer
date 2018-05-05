from collections import deque
import configure as c
tf = {}
idf = {}
word_frequency = {}
interval1 = 1800 * 1000 # 30p
interval2 = c.WINDOW_SIZE * c.TIME_STEP_WIDTH # get rid of tweets of piror 12 windows

def update_wf(word, current_time):
    if word not in word_frequency:
        word_frequency[word] = [deque([]),deque([]),deque([])]
    cwf = word_frequency[word] # current word frequency
    while cwf[1] and cwf[1][0] < current_time - interval1: # hnt: cwf[1]: contain published time of words in 30 minutes
        cwf[0].append(cwf[1].popleft())
    while cwf[0] and cwf[0][0] < current_time - interval2: #hnt: cwf[0]: contain published time of words in 60 minutes
        cwf[0].popleft()

def increase_wf(word, current_time):
    update_wf(word, current_time)
    update_wf('_T', current_time)
    word_frequency[word][1].append(current_time)
    word_frequency['_T'][1].append(current_time)

def get_wf(word, current_time):
    update_wf(word, current_time)
    update_wf('_T', current_time)
    cwf = word_frequency[word]
    twf = word_frequency['_T']
    return (
            len(cwf[0]) * 1.0 / len(twf[0]),
            len(cwf[1]) * 1.0 / len(twf[1])
    ) 

def increase_tf(word, current_time):
    return

def update_idf(current_time):
    for word in idf:
        while idf[word] and idf[word][0] < current_time - c.WINDOW_SIZE * c. TIME_STEP_WIDTH:
            idf[word].popleft()
            if(idf[word] == None):
                del idf[word]
    return idf

def increase_idf(word, current_time):
    if word not in idf:
        idf[word] = deque([])
    idf[word].append(current_time)
    return

def increase_NofTweets(current_time):
    if '_T_' not in idf:
        idf['_T_'] = deque([])
    idf['_T_'].append(current_time)
    
def getNumberOfTweets():
    if idf['_T_']:
        return len(idf['_T_'])
    return 0