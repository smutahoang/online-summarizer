import configure as c
import time
from Tweet import Tweet
import init as g
from init import add_tweet_to_graph, initialize, get_and_update, show_summaries
from heapq import heappush, heappop, nlargest
from collections import defaultdict
from score import get_score
import math
import frequency
import tweet_processing
currentTweets = []


def getSetOfKeywords(currentTime):
    if(c.KEYWORD_SCHEME == c.KeywordGettingScheme.TFIDF):
        return getKeywordsUsingTfIdfs(currentTime)
    elif (c.KEYWORD_SCHEME == c.KeywordGettingScheme.PAGERANK):
        return getKeywordsUsingPageRank (currentTime)
    else:
        return getKeywordsUsingTrendingTopic(currentTime)


def getKeywordsUsingTfIdfs(currentTime):
    heap = []
    keywords = []

    frequency.update_idf(currentTime)
    sumOfFreq = 0
    for word in frequency.idf:       
        if(word in g.ww):
            sumOfFreq += g.ww[word]
            
    for word in frequency.idf:
        if(word in g.ww):
            if(frequency.getNumberOfTweets() == 0 or sumOfFreq == 0 or len(frequency.idf[word]) == 0):
                continue
            # print("tf: %f, sumTf: %f, #tweets: %d, #idf: %d" %(g.ww[word], sumOfFreq,frequency.getNumberOfTweets(), len(frequency.idf[word])))         
            tfIdf = (g.ww[word] / sumOfFreq) * math.log2(frequency.getNumberOfTweets() / len(frequency.idf[word]))
            heappush(heap, (-tfIdf, word))
   
    k = 0
    while (k < c.NUMBER_OF_KEYWORDS and heap != None):
        (tfIdf, word) = heappop(heap)
        keywords.append(word)
        k = k + 1
    
    return keywords


def getKeywordsUsingPageRank(currentTime):
    termImportance = {}
    newTermImportance = {}
    for node in g.ng:
        termImportance[node] = 1 / len(g.ng)
        
    # compute pagerank
    for i in range(c.MAX_ITERATIONS):
        for node in g.ng:
            newTermImportance[node] = (1 - c.DAMPING_FACTOR) / len(g.ng)
        for node in g.ng:
            if node[0] == '_S' or node not in g.ing.keys():
                continue
            
            incomingNodes = g.ing[node]
            for inNode in incomingNodes:
                newTermImportance[node] += c.DAMPING_FACTOR * termImportance[inNode] / len(g.ng[inNode])
        
        for node in g.ng:
            termImportance[node] = newTermImportance[node]
    
    pageRank = [(node, score) for node, score in termImportance.items() if node[0] != '_S']
    pageRank.sort(key=lambda x: x[1], reverse=True)
    return pageRank


def getKeywordsUsingTrendingTopic(currentTime):
    words = frequency.word_frequency.keys()
    counts = {w: frequency.get_wf(w, g.ts) for w in words}
    counts = {w: fl for w, fl in counts.items()
            if ((fl[1] > 0 and fl[1] > c.KEYWORD_INCREASING_LEVEL * fl[0] and fl[0] != 0) or (fl[0] == 0 and fl[1] > 0.01))}
    # hnt: normalize
    mcounts = [(w, math.log((fl[1] + 0.003) / (max(fl[0], 1) + 0.003))) for w, fl in counts.items()]
    mcounts.sort(key=lambda x:-x[1])
 
    keywords = []
    for key, value in mcounts:
        if(len(keywords) >= c.NUMBER_OF_KEYWORDS):
            break;
        keywords.append(key)
    return keywords


# hnt: finding a summary starting from a bigram, parent_keywords: set of keywords
def build_summary(starting_summary, parent_keywords=[]):
    print("---->expanding paths")
    partial_summary = (
        list(starting_summary),  # summary until this point
        0,  # score until this point
        list(starting_summary)  # starting summary
    )

    partial_summaries = []
    
    # hnt: Min heap, -partial_summary[1]: largest one on the top of heap
    #heappush(partial_summaries, (-partial_summary[1], partial_summary))
    partial_summaries.append(partial_summary)
    completed_summaries = []
    time0 = time.time()
    candidates = []
    while partial_summaries:
        
        # generate potential summaries
        # expand them and keep the best ones
        # hnt: keywords: starting bigram; summary: current partial summaries; summary_score: current score
        #currentScore, (summary, summary_score, keywords) = heappop(partial_summaries)
        (summary, summary_score, keywords) = partial_summaries.pop()
        #print("current partial summary in Heap: ", summary, ", ", summary_score)
        # add words to summary
        # : get all nodes adjacent to the first and last node of the current graph
        add_forward = g.ng.get((summary[-2], summary[-1]), {}).keys()
        add_reverse = g.ing.get((summary[0], summary[1]), {}).keys()

        # compute score for possible next moves 
        # also updates ng
        previous_bigram = tuple(summary[-2:])
        next_options = [
            (
                summary + list(bigr)[1:],
                
                get_score(
                    summary,
                    bigr,
                    get_and_update(3, None, previous_bigram + (bigr[1],), g.ts),
                    previous_bigram,
                    1,
                    list(keywords) + list(parent_keywords)
                ),
                bigr[1]
            )
            
            for bigr in add_forward
            
        ]

        # repeat for reverse links (not elegant, refactor?)
        previous_bigram = tuple(summary[:2])
        next_options += [
            (
                list(bigr)[:1] + summary,
                get_score(
                    summary,
                    bigr,
                    get_and_update(3, None, (bigr[0],) + previous_bigram, g.ts),
                    previous_bigram,
                    2,
                    list(keywords) + list(parent_keywords)
                ),
                bigr[0]
            )
            for bigr in add_reverse if bigr[0] != 0 
        ]

        next_options = nlargest(c.NUMBER_OF_LOCAL_MAX, next_options, key=lambda x: x[1])
        currentIndex = len(partial_summaries)
        for next in next_options:
            summary, score = (
                    next[0],
                    summary_score + next[1]
            )
            #print(score)
            time1 = time.time()
            if summary[-1] == '_E' and summary[0] == '_S' and len(summary) > c.MINIMAL_LENGTH_OF_A_TWEET:
                # this summary looks good, we keep it
                # update penalties
                for w in summary:
                    g.penalty[w] += 1
                #print ("the score of summary: ", score)
                return summary

            elif (summary[-1] == '_E' and summary[0] == '_S'):
                # this summary is too short, discard it
                for w in summary:
                    g.penalty[w] += 1
            elif ((summary[-1] != '_E' or summary[0] != '_S') and len(summary) >= c.MAXIMAL_LENGTH_OF_A_TWEET):
            # this path is too long, discard it
                for w in summary:
                    g.penalty[w] += 1
            elif summary.count(summary[0]) == c.MAXIMAL_OCCURRENCE_OF_A_WORD or summary.count(summary[-1]) == c.MAXIMAL_OCCURRENCE_OF_A_WORD:
                for w in summary:
                    g.penalty[w] += 1                
#             elif (time1 - time0 > c.MAXIMAL_TIME_FOR_GETTING_A_TWEET):
#                 for w in summary:
#                     g.penalty[w] += 1
#                 return None
            else:
                if(summary not in candidates):
                    
                    #heappush(partial_summaries, (-score, (summary, score, keywords)))
                    partial_summaries.insert(currentIndex, (summary, score, keywords))
                    candidates.append(summary)
                    #print("----> next candidates in heap:", summary, ", ", (score))
                    
    # no summary could be built
    return None


def summarize_keywords(createAt, nOfTweetsInSummary, currentTime, expand=True):
    summaries = []
    g.penalty = defaultdict(lambda: 0)
    keywords = set()
    if(c.KEYWORD_SCHEME == c.KeywordGettingScheme.TFIDF):
        keywords = getKeywordsUsingTfIdfs(createAt)
        bigrams = [b for b in g.nw.items() if b[0][0] in keywords or b[0][1] in keywords]
        
    elif(c.KEYWORD_SCHEME == c.KeywordGettingScheme.TRENDINGTOPIC):
        if(currentTime == 1):
            keywords = getKeywordsUsingTfIdfs(createAt) 
        else: 
            keywords = getKeywordsUsingTrendingTopic(createAt)
        bigrams = [b for b in g.nw.items() if b[0][0] in keywords or b[0][1] in keywords]
        
    else:
        bigrams = getKeywordsUsingPageRank(createAt)
        k = 0; i = 0
        while i < c.NUMBER_OF_KEYWORDS and i < len(bigrams):
            if(bigrams[i][0][0] not in tweet_processing.stopWords and bigrams[i][0][0] not in keywords):
                keywords.add(bigrams[i][0][0])
                #k = k + 1
            if(bigrams[i][0][1] not in tweet_processing.stopWords and bigrams[i][0][1] not in keywords):
                keywords.add(bigrams[i][0][1])
                #k = k + 1
            i = i + 1
    print("keyword: ", keywords)
    print("--> generate summary:")
    count = 0
    while len(summaries) < nOfTweetsInSummary:
        # select top starting bigrams that contain one of the keywords
        # to use as seeds for the sentences
        # put bigrams containing '_S' or '_E' further down the list
        # hnt: bigrams: list of bigrams containing one of keywords
        
        start = max(bigrams, key=lambda x: \
                x[1] - 10 * g.penalty[x[0][0]] - 10 * g.penalty[x[0][1]] - 
                (0 if x[0][0] != '_S' and x[0][1] != '_E' else 100))

        start = start[0]
        print("keyword: %s", ', '.join(start))
        summary = build_summary(start, keywords)
        #print("-->", summary)
        if summary:
            summaries.append(summary)
        count = count + 1
    show_summaries(summaries, currentTime, keywords=start)


def getElapsedTime(currentTime, refTime, stepWidth):
    if (currentTime <= refTime):
        return 0
    
    return (int) ((currentTime - refTime) / stepWidth)


def main() :
    file = open(c.INPUT_FILE, encoding="utf8")
    startTime = time.time()
    nextUpdate = 0;
    nTweet = 0;
    
    time0 = time.time()
    # iterate tweets in file
    for line in file:
        
        nTweet = nTweet + 1
        
        text = line.split("\t")
        createAt = int(text[2])  # time
        id = text[3]
        content = text[4]
        tweet = Tweet(createAt, id, content)
        # currentTweets.append(tweet)
        if nTweet == 1:
            nextUpdate = createAt + c.TIME_STEP_WIDTH
            initialize(tweet)
            refTime = createAt
        currentTime = getElapsedTime(tweet.createAt, refTime, c.TIME_STEP_WIDTH);
        
        add_tweet_to_graph(tweet)
        print("------------------>tweet: %s" %(tweet.text.encode('utf-8')))
        # generate summary
        if (c.UPDATING_TYPE == c.UpdatingScheme.PERIOD and createAt >= nextUpdate):
            print("+++++++++++++++++++++++update+++++++++++++++++++++++++++++")
            print("Number of tweets up to the current time: %d" % (nTweet))
            nextUpdate = createAt + c.TIME_STEP_WIDTH
            print("Number of nodes: %d" % (len(g.nw)))
            time1 = time.time()
        
            if(currentTime > c.WINDOW_SIZE):
                g.prune(g.ts)  # pruning to get rid of some unimportant keywords
           
            time2 = time.time()
            for item in g.nw.items():  # iterate each node in the graph
                get_and_update(2, g.nw, item[0], g.ts)  # apply decaying window
           
            time3 = time.time()
           
            print("----->currentTime: %d" % currentTime)
            summarize_keywords(g.ts, c.NUMBER_OF_TWEETS, currentTime)
            
            time5 = time.time()

            print ('----------------------------')
            
            if(c.DEBUG == 1):
                print("--> time for reading: %s (s)" % (time1 - time0))
                print("--> time for pruning: %s (s)" % (time2 - time1))
                print("--> time for decaying: %s (s)" % (time3 - time2))
                # print("--> time for getting keyword: %s (s)" %(time4 - time3))
                print("--> time for summarizing: %s (s)" % (time5 - time3))
            time0 = time.time()
    file.close()
    
    endTime = time.time()
    print("Running time: %f (s)" % (endTime - startTime))
    return


main()

