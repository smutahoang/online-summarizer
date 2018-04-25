import configure as c
import validators


stopWords = set()
braces = set() 
punctuations = set()
quoteSymbols = set()
validSuffixSymbols = set()
validPrefixSymbols = set()

def getStopWords():
   

    file = open("{}/common-english-adverbs.txt".format(c.STOPWORD_PATH))

    for line in file:
        tokens = line.lower().split(",");
        for i in range(len(tokens)):
            stopWords.add(tokens[i].replace("\n", ""));
    file.close();

    file = open("{}/common-english-prep-conj.txt".format(c.STOPWORD_PATH))
    for line in file:
        tokens = line.lower().split(",");
        for i in range(len(tokens)):
            stopWords.add(tokens[i].replace("\n", ""));

    file.close();
    
    
    file = open("{}/common-english-words.txt".format(c.STOPWORD_PATH));
    for line in file:
        tokens = line.lower().split(",")
        for i in range(len(tokens)):
            stopWords.add(tokens[i].replace("\n", ""));
    file.close();

    file = open("{}/smart-common-words.txt".format(c.STOPWORD_PATH))
    
    for line in file:
        tokens = line.lower().split(",");
        for i in range(len(tokens)):
            stopWords.add(tokens[i].replace('\n', ''));
      
    file.close();

    file = open("{}/mysql-stopwords.txt".format(c.STOPWORD_PATH))

    for line in file:
        tokens = line.lower().split(",");
        for i in range(len(tokens)):
            stopWords.add(tokens[i].replace("\n", ""));
     
    file.close();

    file = open("{}/twitter-slang.txt".format(c.STOPWORD_PATH))
    
    for line in file:
        tokens = line.lower().split(",");
        for i in range(len(tokens)):
            stopWords.add(tokens[i].replace("\n", ""));
       
    file.close();

    file = open("{}/shorthen.txt".format(c.STOPWORD_PATH))

    for line in file:
        tokens = line.lower().split(",");
        for i in range(len(tokens)):
            stopWords.add(tokens[i].replace("\n", ""));

    file.close();
   
    addMoreStopWords();
    return

def addMoreStopWords():
    # words due to truncated tweets
    stopWords.add("//t");
    stopWords.add("http");
    stopWords.add("https");
    return
    
def extractTermInTweet(inputText):
    init()
    chars = list(inputText)
    
    
    removeNewLineAndTabCharacter(chars)
   
    removeOriginalAuthors(chars)
    
    removeHTMLsymbols(chars)
    
    removeQuotationSymbols(chars)
    
    removePunct(chars)
    
    i = 0;
    while (i < len(chars)):
        j = getWord(chars, i);
        if (j == i):
            i = i+1
            continue;
      
        if (isNumber(chars, i, j)):
            i = j;
        elif (isHour(chars, i, j)):
            i = j;
        elif(isURL(chars, i, j)):
            i = j;
        elif (isEnglish(chars, i, j) == False) :
            for p in range(i, j):
                chars[p] = ' '
            i = j;
        else:
            for p in range(i, j):
                if chars[p] in punctuations:
                    chars[p] = ' ';
                else:
                    chars[p] = chars[p].lower()
            removeSymbolInWord(chars, i, j);
            i = j;

    

    terms = []
    i = 0;
    while (i < len(chars)):
        j = getWord(chars, i)
       
        if (j == i):
            i = i+1
            continue;
        
        if (containCharacterORNumber(chars, i, j)):
            term = ''.join(chars[i:j])
            if (term not in stopWords):
                terms.append(term)
        i = j;
    return terms 
    
    
def removeSymbolInWord(chars, start, end) :

    # ptScreen(chars);
    # System.out.printf("\ni = %d, j = %d", start, end);

    i = end - 1
    while ((chars[i].isdigit() or chars[i].isalpha())==False):
        if (chars[i] in validSuffixSymbols):
            break
        chars[i] = ' '
        i = i -1
        if (i <= start):
            return

    i = start;
    while ((chars[i].isdigit() or chars[i].isalpha()) == False):
        if (chars[i] in validPrefixSymbols):
            break
        chars[i] = ' '
        i = i+1
        if (i >= end):
            return
    return
    
    
def containCharacterORNumber(chars, start, end):
    for i in range(start, end):
        if (chars[i].isdigit() or chars[i].isalpha()):
            return True
    return False

def isNumber(chars, start, end):
    for i in range(start, end):
        if (chars[i].isdigit()):
            continue
        if (chars[i] == '.'):
            continue;
        if (chars[i] == ','):
            continue
        return False
    return True

def isHour(chars, start, end):
    for i in range(start, end):
        if chars[i].isdigit():
            continue
        if chars[i] == ':':
            continue
        return False
    return True;

def isURL(text, i, j):
    return validators.url(''.join(text[i:j]))

def isEnglish(chars, start, end):
    for i in range(start, end):
        if (ord(chars[i]) > 128):
            return False
    return True
    
def getWord(chars, i):
    j = i;
    while (True):
        if (j >= len(chars)):
            break;
        elif(chars[j] == ' '):
            break;
        else:
            j = j+1
    return j;

    
# def removeNewLineAndTabCharacter(chars):
#     chars = chars.replace('\n', ' ')
#     chars = chars.replace('\t', ' ')
#     return chars


def initQouteSymbols():
    global quoteSymbols
    quoteSymbols.add('\"');
    quoteSymbols.add('\'');
    quoteSymbols.add('`');
    quoteSymbols.add('\u2014') # long dash
    quoteSymbols.add('\u0022');
    quoteSymbols.add('\u00bb'); # right-pointing double-angle quotation
                                # mark
    quoteSymbols.add('\u2018'); # left single quotation mark
    quoteSymbols.add('\u2019'); # right single quotation mark
    quoteSymbols.add('\u201a'); # single low-9 quotation mark
    quoteSymbols.add('\u201b'); # single high-reversed-9 quotation mark
    quoteSymbols.add('\u201c'); # left double quotation mark
    quoteSymbols.add('\u201d'); # right double quotation mark
    quoteSymbols.add('\u201e'); # double low-9 quotation mark
    quoteSymbols.add('\u201f'); # double high-reversed-9 quotation mark
    quoteSymbols.add('\u2039'); # single left-pointing angle quotation mark
    quoteSymbols.add('\u203a'); # single right-pointing angle quotation
                                # mark
    quoteSymbols.add('\u300c'); # left corner bracket
    quoteSymbols.add('\u300d'); # right corner bracket
    quoteSymbols.add('\u300e'); # left white corner bracket
    quoteSymbols.add('\u300f'); # right white corner bracket
    quoteSymbols.add('\u301d'); # reversed double prime quotation mark
    quoteSymbols.add('\u301e'); # double prime quotation mark
    quoteSymbols.add('\u301f'); # low double prime quotation mark
    quoteSymbols.add('\ufe41'); # presentation form for vertical left
                                # corner bracket
    quoteSymbols.add('\ufe42'); # presentation form for vertical right
                                # corner bracket
    quoteSymbols.add('\ufe43'); # presentation form for vertical left
                                # corner white bracket
    quoteSymbols.add('\ufe44'); # presentation form for vertical right
                                # corner white bracket
    quoteSymbols.add('\uff02'); # fullwidth quotation mark
    quoteSymbols.add('\uff07'); # fullwidth apostrophe
    quoteSymbols.add('\uff62'); # halfwidth left corner bracket
    quoteSymbols.add('\uff63'); # halfwidth right corner bracket


def removeNewLineAndTabCharacter(chars):
    for i in range(len(chars)):
        if (chars[i] == '\n') :
            chars[i] = ' ';
            continue;
        elif (chars[i] == '\r'):
            chars[i] = ' ';
            continue;
        elif(chars[i] == '\t'):
            chars[i] = ' ';
            continue;
        else:
            continue;
    return

def isURLStart(chars, i) :
    if (i >= len(chars) - 4):
        return False;
    if (chars[i] != 'h'):
        return False;
    if (chars[i + 1] != 't'):
        return False;
    if (chars[i + 2] != 't'):
        return False;
    if (chars[i + 3] != 'p'):
        return False;
    return True;


def removePunct(chars): 
    for i in range(len(chars)):
        if (chars[i] in punctuations): # ignore removing ending tokens
            if (i == 0): #first character
                chars[i] = ' ';
                continue;
            elif (i == len(chars) - 1): #last character
                chars[i] = ' ';
                continue;
            elif(chars[i - 1] == ' '): #first character of the word
                chars[i] = ' ';
                continue;
            elif (chars[i + 1] == ' '): #last character of the word
                chars[i] = ' ';
                continue;
            elif (isURLStart(chars, i + 1)): #right before url
                chars[i] = ' ';
                continue;
            elif (chars[i] == '.'): #do nothing, in case of url
                continue;
            elif (chars[i] == ':'): #do nothing, in case of url
                continue;
            elif (chars[i-1].isdigit() == False):
                chars[i] = ' ';
                continue;
            elif (chars[i+1].isdigit() == False):
                chars[i] = ' ';
                continue;
            else:
                # do nothing
                continue;
    return

def initPunctuations():
    global punctuations
    punctuations = set()
    punctuations.add('~');
    punctuations.add('^');
    punctuations.add('(');
    punctuations.add(')');
    punctuations.add('{');
    punctuations.add('}');
    punctuations.add('[');
    punctuations.add(']');
    punctuations.add('<');
    punctuations.add('>');
    punctuations.add(':');
    punctuations.add(';');
    punctuations.add(',');
    punctuations.add('.');
    punctuations.add('?');
    punctuations.add('!');
    return 

def removeQuotationSymbols(chars):    
    for i in range(len(chars)):
        if (chars[i] in quoteSymbols):
            if (i == 0) : #first character
                chars[i] = ' ';
                continue;
            elif (i == len(chars) - 1) : #last character
                chars[i] = ' ';
                continue;
            elif (chars[i - 1] == ' ') : #first character of the word
                chars[i] = ' ';
                continue;
            elif (chars[i + 1] == ' ') : #last character of the word
                chars[i] = ' ';
                if (chars[i - 1] == 's'): #for the case, e.g., "mothers'"
                    chars[i - 1] = ' ';
                continue;
            elif (chars[i + 1] == 's'): #for the case, e.g.,
                                                # "mother's"
                chars[i] = ' ';
                chars[i + 1] = ' ';
            elif (i < len(chars) - 2):
                if (chars[i + 2] == ' '): #for the case, e.g., "don't"
                    continue;
            elif (isShorten(chars, i)):
                continue;
            else:
                chars[i] = ' ';
    return

def isShorten(chars, i) :
    if (chars[i] not in quoteSymbols):
        return False;
    if (i <= len(chars) - 3):
        if (chars[i + 1] == 'r' and chars[i + 2] == 'e'): #e.g, "they're"
            return True;
        if (chars[i + 1] == 'v' and chars[i + 2] == 'e'): #e.g, "they've"
            return True;
        if (chars[i + 1] == 'l' and chars[i + 2] == 'l'): #e.g, "she'll"
            return True;
    elif(i <= len(chars) - 2):
        if (chars[i + 1] == 'm'): # e.g, "I'm"
            return True;
        if (chars[i + 1] == 'd'): # e.g, "it'd"
            return True;
        if (chars[i + 1] == 't'): # e.g, "it'd"
            return True;
    return False;

def removeHTMLsymbols(chars):
    for i in range(len(chars)):
        if (chars[i] == '&') : #html chatacter
            j = i;
            while (j < len(chars)):
                if (chars[j] == ' '):
                    break
                elif (chars[j] in punctuations):
                    break
                elif(chars[j] in validPrefixSymbols):
                    break
                else:
                    chars[j] = ' '
                    j = j+1
            i = j
    return
    
def removeOriginalAuthors(chars):
    for i in range(len(chars)):
        if (i > len(chars) - 4):
            return
        if (chars[i].lower() != 'r'):
            continue;
        if (chars[i + 1].lower() != 't'):
            continue;
        if (chars[i + 2] != ' '):
            continue;
        if (chars[i + 3] != '@'):
            continue;
        if (i > 0):
            if (chars[i - 1] != ' '):
                continue;
        j = i + 4;
        while (j < len(chars)):
            if (chars[j] == ' '):
                break;
            j=j+1
        
        for p in range(i, j):
            chars[p] = ' ';
    return

def initBraces():
    
    braces.add('~');
    braces.add('^');
    braces.add('(');
    braces.add(')');
    braces.add('{');
    braces.add('}');
    braces.add('[');
    braces.add(']');
    braces.add('<');
    braces.add('>');
    return

def initPrefixSuffixSymbols():
    
    validPrefixSymbols.add('@');
    validPrefixSymbols.add('#');
    validPrefixSymbols.add('%');
    validPrefixSymbols.add('$');

    
    validSuffixSymbols.add('%');
    validSuffixSymbols.add('$');
    return


def init():
    
    
    initPunctuations()
    initBraces();
    initQouteSymbols();
    initPrefixSuffixSymbols();

    getStopWords();
    return

# def main():
#     
#     message = "__the _federal lawsuit will be filed on behalf of more than 20 individuals  #muslimban https://t.co/lDUfnbSLpn";
#     print("message:", message)
#     result = extractTermInTweet(message)
#     print("", result)
    





    