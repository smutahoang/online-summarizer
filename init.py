from tokenizer import tokenize
from frequency import get_wf, increase_wf
import configure as c
from collections import defaultdict

# simple function to print the summaries
def show_summaries(summaries, keywords=None):
    for summary in summaries:
        l = len(summary) - 2
        if keywords:
            print ('%s (%s): %s' % (l, ','.join(keywords), ' '.join(summary[1:-1])))
        else:
            print ('%s: %s' % (l, ' '.join(summary[1:-1])))

def initialize(tweet):
    global nw # node-weight: weights for each bigram
    global ng # node-graph: forward links from a bigram to the next one, along with weights
    global ing # inverse-node_graph: backward links froma bigram to the previous one, +weights
    global ts # timestamp
    global ww # word-weight: weights for each word
    global penalty # penalties for words already used in summaries
    global start_time #
    global cm # correlation matrix
    global last_prune
    global last_update
    global word_frequency
    global inverted_tweet_frequency
    start_time = tweet.createAt
    last_prune = start_time # --> check
    
    # initialize graph structure
    word_frequency = {}
    inverted_tweet_frequency = {}
    ww = {}
    nw = {}
    ng = {}
    ing = {}
    cm = {}
    last_update = {} # --> check
    # this penalty will be used to prevent from using 
    # the same words in all summaries
    #TODO: cum fac delay pe penalty?
    penalty = defaultdict(lambda: 0) # --> check
    return

def  add_tweet_to_graph(tweet):
    global ts
    global last_prune
    global word_frequency
    global inverted_tweet_frequency
    
        
    # Tokenize tweets, split in sentences
    # and add markers for beginning and end of sentence
    sentences = []
    for sentence in tokenize(tweet.text):
        sentence = ['_S'] + sentence + ['_E']
        sentences.append(sentence)
        
    # compute word frequencies
    for sentence in sentences:
        for word in sentence:
            if word == '_S' or word == '_E' or word == 'rt':
                continue
            if word in word_frequency: 
                word_frequency[word] += 1 
            else: 
                word_frequency[word] = 1
            if word not in inverted_tweet_frequency:
                inverted_tweet_frequency[word] = []
            if tweet.id not in inverted_tweet_frequency[word]:
                inverted_tweet_frequency[word].append(tweet.id)

    # compute word weight
    for sentence in sentences:
        for word in sentence:
            add_one(1, word, tweet.createAt)
        
    # compute node (bigram) weight
    for sentence in sentences:
        for i in range(len(sentence) - 1):
            add_one(2, (sentence[i], sentence[i + 1]), tweet.createAt)
        
    # compute word graph using bigrams
    for sentence in sentences:
        for i in range(len(sentence) - 2):
            item = (sentence[i], sentence[i + 1], sentence[i + 2])
            add_one(3, item, tweet.createAt)
            
    # compute correlation matrix between words
    # will be used in computing a sentence score
    for sentence in sentences:
        for i in range(len(sentence) - 1):
            w1 = sentence[i]
            for j in range(i + 1, len(sentence)):
                add_one(4, (sentence[i], sentence[j]), tweet.createAt)

    # prune?
    #if t['ts'] > last_prune + forget_last_update:
    #    last_prune = t['ts']
    #    prune(t['ts'])
                    
    ts = tweet.createAt

    
# the next lines are used for the sliding window
# the table multpl is used for memoization
# the function wraps things up
multpl_values = [1]

def get_multpl(item, current_time):
    if type(item) == tuple:
        item = ','.join(item) # to use less space

    if item not in last_update:
        last_update[item] = start_time
    diff = int(current_time - last_update[item])
    last_update[item] = current_time
    while len(multpl_values) <= diff:
        multpl_values.append(multpl_values[-1] * c.MULTPL)
    return multpl_values[diff]

def add_one(case, item, current_time):
    if case == 1:
        ww[item] = ww.get(item, 0) * get_multpl(item, current_time) + 1
        
    elif case == 2:
        nw[item] = nw.get(item, 0) * get_multpl(item, current_time) + 1
        
    elif case == 3:
        bigram1 = (item[0], item[1])
        bigram2 = (item[1], item[2])
        if bigram1 not in ng:
            ng[bigram1] = {}
        ng[bigram1][bigram2] = \
            ng[bigram1].get(bigram2, 0) * get_multpl(item, current_time) + 1
        # Also update the inverse node graph
        if bigram2 not in ing:
            ing[bigram2] = {}
        ing[bigram2][bigram1] = ng[bigram1][bigram2]

    elif case == 4:
        safe_item = ('_C', item[0], item[1])
        if safe_item[1] not in cm:
            cm[safe_item[1]] = defaultdict(int)
        cm[safe_item[1]][safe_item[2]] *= get_multpl(safe_item, current_time)
        cm[safe_item[1]][safe_item[2]] += 1

def get_and_update(case, structure, item, current_time):
    if case in [1, 2]:
        structure[item] *= get_multpl(item, current_time)
        return structure[item]
        
    elif case == 3: # interested in a forward or backward link
        bigram1 = (item[0], item[1])
        bigram2 = (item[1], item[2])
        ng[bigram1][bigram2] *= get_multpl(item, current_time)
        ing[bigram2][bigram1] = ng[bigram1][bigram2]
        return ng[bigram1][bigram2]

    elif case == 4:
        safe_item = ('_C', item[0], item[1])
        cm[safe_item[1]][safe_item[2]] *= get_multpl(safe_item, current_time)
        return cm[safe_item[1]][safe_item[2]]

def prune(current_time):
    print ('pruning at %s' % current_time)
    global last_update

    # remove old items from last_update
    removed = [
            tuple(k.split(',')) for k, v in last_update.items() \
            if v <= current_time - c.WINDOW_SIZE * c.TIME_STEP_WIDTH
    ]
    last_update = {
            k: v for k, v in last_update.items() \
            if v > current_time - c.WINDOW_SIZE * c.TIME_STEP_WIDTH
    }

    for item in removed:
        try:
            if len(item) == 1:
                del ww[item[0]]

            elif len(item) == 2:
                del nw[item]

            elif len(item) == 3:
                if item[0] in '_C':
                    del cm[item[1]][item[2]]
                    if not cm[item[1]]:
                        del cm[item[1]]
                else:
                    bigram1 = (item[0], item[1])
                    bigram2 = (item[1], item[2])
                    del ng[bigram1][bigram2]
                    del ing[bigram2][bigram1]
                    if not ng[bigram1]:
                        del ng[bigram1]
                    if not ing[bigram2]:
                        del ing[bigram2]
            else:
                raise Exception('big')
        except Exception as e:
            print (item)
            raise e
