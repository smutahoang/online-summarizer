INPUT_FILE = "travelBan_2017-01-27_graphFilteredTweets.txt"
NUMBER_OF_TWEETS = 10

TIME_STEP_WIDTH = 60*60*1000

UPDATING_TYPE = "PERIOD"

TWEET_WINDOW = 1000
WINDOW_SIZE = 12
NUMBER_OF_KEYWORDS = 5

# some constants
# multpl is 1 - c # see mining massive datasets book for theory
# 0.0025 - provides a very short window - 15 minutes
# 0.0005 - 1h window
# 0.00005 - 10h window
MULTPL = 1 - 0.0005