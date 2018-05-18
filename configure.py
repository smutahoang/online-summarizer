
def enum(**enums):
    return type('Enum', (), enums)

# constants for directories and options
INPUT_FILE = "C:/Users/Huyen Nguyen/eclipse-workspace/OnlineSummarizer/data/input/travelBan_2017-01-27_graphFilteredTweets.txt"
STOPWORD_PATH = "C:/Users/Huyen Nguyen/eclipse-workspace/OnlineSummarizer/data/stopwords";
OUTPUT_PATH = "C:Users/Huyen Nguyen/eclipse-workspace/OnlineSummarizer/data/output/baselines/online"

UpdatingScheme = enum(PERIOD = 'PERIOD', TWEET_COUNT = 'TWEET_COUNT')
KeywordGettingScheme = enum(TFIDF = 'TFIDF', PAGERANK = 'PAGERANK', TRENDINGTOPIC = 'TRENDINGTOPIC')
MAXIMAL_TIME_FOR_GETTING_A_TWEET = 10*60
MAXIMAL_OCCURRENCE_OF_A_WORD = 3

MAXIMAL_LENGTH_OF_A_TWEET = 20
MINIMAL_LENGTH_OF_A_TWEET = 8
# constants for summarization
NUMBER_OF_TWEETS = 20 # #tweets in final summarization for each sliding window
TIME_STEP_WIDTH = 60 * 60 * 1000  # 1 hour
WINDOW_SIZE = 12
UPDATING_TYPE = UpdatingScheme.PERIOD
KEYWORD_SCHEME = KeywordGettingScheme.TFIDF
NUMBER_OF_LOCAL_MAX = 2

TWEET_WINDOW = 1000
DEBUG = 1
# some constants
# multpl is 1 - c # see mining massive datasets book for theory
# 0.0025 - provides a very short window - 15 minutes
# 0.0005 - 1h window
# 0.00005 - 10h window
MULTPL = 1 - 0.0005

NUMBER_OF_KEYWORDS = 20
# constants for getting keywords using tf-idf

# constants for getting keywords using trending topic based approach
CURRENT_KEYWORD_WINDOW = 60* 60 * 1000 # 40P
PREVIOUS_KEYWORD_WINDOW = 120 * 60 * 1000 # 2 day
KEYWORD_INCREASING_LEVEL = 2.5  # frequency of word in current window = 2* frequency in previous window
NORMALIZING_FACTOR = 0.003  # normalize the novelty's s of keywords

# constants for getting keywords using PageRank
DAMPING_FACTOR = 0.85
MAX_ITERATIONS = 20;










