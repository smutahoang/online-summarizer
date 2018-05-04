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

currentTweets = []


def getSetOfKeywords(currentTime):
    words = frequency.word_frequency.keys()
    counts = {w: frequency.get_wf(w, g.ts) for w in words}
    counts = {w: fl for w, fl in counts.items()
            if ((fl[1] > 0 and fl[1] > c.KEYWORD_INCREASING_LEVEL * fl[0] and fl[0] !=0) or (fl[0] == 0 and fl[1] > 0.01))}
    # hnt: normalize
    mcounts = [(w, math.log((fl[1] + 0.003) / (max(fl[0],1) + 0.003))) for w, fl in counts.items()]
    mcounts.sort(key = lambda x: -x[1], reverse = True)
 
    keywords = []
    for key, value in mcounts:
        if(len(keywords) > c.NUMBER_OF_KEYWORDS):
            break;
        keywords.append(key)
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
            for bigr in add_reverse if bigr[0] != 0
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

    bigrams = [b for b in g.nw.items() if b[0][0] in keywords or b[0][1] in keywords]
    while len(summaries) < n:
        # select top starting bigrams that contain one of the keywords
        # to use as seeds for the sentences
        # put bigrams containing '_S' or '_E' further down the list
        # hnt: bigrams: list of bigrams containing one of keywords
        
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
    
    time0 = time.time()
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
            time1 = time.time()
            if(currentTime > c.WINDOW_SIZE):
                g.prune(g.ts)  # pruning to get rid of some unimportant keywords
            time2 = time.time()
            for item in g.nw.items():  # iterate each node in the graph
                get_and_update(2, g.nw, item[0], g.ts)  # apply decaying window
            
            time3 = time.time()
    
            keyword_set = getSetOfKeywords(createAt)
            time4 = time.time()
            print ("keywords: " , keyword_set)
           
            print("----->currentTime: %d" % currentTime)
            summarize_keywords(keyword_set, 3, currentTime)
            time5 = time.time()

            print ('----------------------------')
            
            if(c.DEBUG == 1):
                print("--> time for reading: %s (s)" % (time1 - time0))
                print("--> time for pruning: %s (s)" % (time2 - time1))
                print("--> time for decaying: %s (s)" % (time3 - time2))
                print("--> time for getting keyword: %s (s)" % (time4 - time3))
                print("--> time for summarizing: %s (s)" % (time5 - time4))
            time0 = time.time()
    file.close()
    
    endTime = time.time()
    print("Running time: %f (s)" % (endTime - startTime))
    return

# read the first tweet


main()

