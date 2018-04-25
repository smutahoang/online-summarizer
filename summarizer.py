import configure as c
import time
from Tweet import Tweet
import init as g
from init import add_tweet_to_graph, initialize, get_and_update, show_summaries
from heapq import heappush, heappop, nlargest
from collections import defaultdict
from score import get_score
import math

currentTweets = []


def getSetOfKeywords():
    heap = []
    keywords = []
    total = 0
    for word, freq in g.word_frequency.items():
        total += freq
    for word, freq in g.word_frequency.items():
        tfIdf = (freq / total) * math.log2(len(currentTweets) / len(g.inverted_tweet_frequency[word]))
        heappush(heap, (-tfIdf, word))
   
    k = 0
    while (k < c.NUMBER_OF_KEYWORDS and heap != None):
        (tfIdf, word) = heappop(heap)
        keywords.append(word)
        k = k + 1
    
    return keywords

# fiding a summary starting from a keyword
def build_summary(starting_summary, parent_keywords=[]):

    partial_summary = (
        list(starting_summary),  # summary until this point
        0,  # score until this point
        list(starting_summary)  # starting summary
    )

    partial_summaries = []
    heappush(partial_summaries, (-partial_summary[1], partial_summary))
    completed_summaries = []

    while partial_summaries:

        # generate potential summaries
        # expand them and keep the best ones
        _, (summary, summary_score, keywords) = heappop(partial_summaries)

        # add words to summary
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
            for bigr in add_reverse if bigr[0]!=0
        ]

        next_options = nlargest(5, next_options, key=lambda x: x[1])

        for next in next_options:
            summary, score = (
                    next[0],
                    summary_score + next[1]
            )
            
            if summary[-1] == '_E' and summary[0] == '_S' and len(summary) > 8:
                # this summary looks good, we keep it
                # update penalties
                for w in summary:
                    g.penalty[w] += 1
                print ("the score of summary: ", score)
                return summary

            elif (summary[-1] == '_E' and summary[0] == '_S'):
                # this summary is too short, discard it
                for w in summary:
                    g.penalty[w] += 1
            else:
                partial_summaries.append((-score, (summary, score, keywords)))

    # no summary could be built
    return None


def summarize_keywords(keywords, n, currentTime, expand=True):
    summaries = []
    g.penalty = defaultdict(lambda: 0)
    keywords = set(keywords)
#     if expand:
#         try:
#             keywords = get_expanded_keywords(keywords)
#         except Exception as e:
#             print(e)
#             return
    bigrams = [b for b in g.nw.items() if b[0][0] in keywords or b[0][1] in keywords]
    while len(summaries) < n:
        # select top starting bigrams that contain one of the keywords
        # to use as seeds for the sentences
        # put bigrams containing '_S' or '_E' further down the list
        #hnt: bigrams: list of bigrams containing one of keywords
        
        
        start = max(bigrams, key=lambda x: \
                x[1] - 10 * g.penalty[x[0][0]] - 10 * g.penalty[x[0][1]] - 
                (0 if x[0][0] != '_S' and x[0][1] != '_E' else 100))

        start = start[0]

        summary = build_summary(start, keywords)

        if summary:
            summaries.append(summary)
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
    
    
    # iterate tweets in file
    for line in file:
        
        nTweet = nTweet + 1
        
        text = line.split("\t")
        createAt = int(text[2])  # time
        id = text[3]
        content = text[4]
        tweet = Tweet(createAt, id, content)
        currentTweets.append(tweet)
        if nTweet == 1:
            nextUpdate = createAt + c.TIME_STEP_WIDTH
            initialize(tweet)
            refTime = createAt
        currentTime = getElapsedTime(tweet.createAt, refTime, c.TIME_STEP_WIDTH);
       
            
        add_tweet_to_graph(tweet)
        # generate summary
        if (c.UPDATING_TYPE == "PERIOD" and createAt >= nextUpdate):
            print("Number of tweets up to the current time: %d" % (nTweet))
            nextUpdate = createAt + c.TIME_STEP_WIDTH
            print("Number of nodes: %d" % (len(g.nw)))
            g.prune(g.ts)  # pruning to get rid of some unimportant keywords
            for item in g.nw.items():  # iterate each node in the graph
                get_and_update(2, g.nw, item[0], g.ts)  # apply decaying window
            
    
            keyword_set = getSetOfKeywords()
            print ("keywords: " , keyword_set)
            runtime = time.time()
            print("----->currentTime: %d" %currentTime)
            summarize_keywords(keyword_set, 3, currentTime)
            runtime = time.time() - runtime
            print ('(%s)' % runtime)
            print ('----------------------------')

    file.close()
    
    endTime = time.time()
    print("Running time: %fms" % (endTime - startTime))
    return

# read the first tweet

main()

