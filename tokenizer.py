import re


def tokenize(original_text):
    text = original_text.lower()
    
    # Encodings....
    chars = {
        u'\xe9': 'e',
        u'\xe1': 'a',
    }
    for fr, to in chars.items():
        text = text.replace(fr, to)
    
    #text = re.sub(r'\\\\', r'\\', text)
    text = re.sub(r'\\\\', r'\\', text)
    text = re.sub(r'\\x\w{2,2}', ' ', text)
    text = re.sub(r'\\u\w{4,4}', ' ', text)
    text = re.sub(r'\\n', ' . ', text)
    
    # special rules for my ElClasico dataset
    pairs = {
        'elclasico': 'el clasico',
        'realmadrid': 'real madrid',
        'fcbarcelona': 'fc barcelona',
    }
    for fr, to in pairs.items():
        text = text.replace(fr, to)
    
    # Remove urls
    #text = re.sub(r'\w+:\/\/\S+', r' \n ', text) #hnt: dont remove urls
    
    # Ignore usernames and hashtags
    text = text.replace('@', ' ')
    text = text.replace('#', ' ')
    
    # Other fixes
    text = text.replace('&gt;', ' ')
    text = text.replace('&lt;', ' ')
    text = text.replace('&', ' and ')
    text = text.replace('*', ' ')
    text = text.replace(' v ', ' vs ')
    text = text.replace(' vs. ', ' vs ')
    
    # Smileys..
    text = text.replace(':d', ' ')
    
    # Format whitespaces
    text = text.replace('"', ' ')
    text = text.replace('\'', ' ')
    text = text.replace('_', '')
    text = text.replace('-', ' ')
    text = text.replace('=', ' ')
    text = re.sub(' +',' ', text)
    
    # Remove repeated (3+) letters: cooool --> cool, niiiiice --> niice 
    text = re.sub(r'([a-zA-Z])\1\1+(\w*)', r'\1\1\2', text)
    # Do it again in case we have coooooooollllllll --> cooll
    text = re.sub(r'([a-zA-Z])\1\1+(\w*)', r'\1\1\2', text)
    
    # Split in phrases
    phrases = re.split(r'[?!;\.()\n]', text) #dont split sentence when reading :
    #phrases = re.split(r'[?!;:\.()\n]', text)
    phrases = [re.findall(r'[\w%\*&#]+', ph) for ph in phrases]
    phrases = [ph for ph in phrases if ph]
    
    return phrases

# hnt
def mainTest():
    text = "RT @amyharvard_: The federal lawsuit will be filed on behalf of more than 20 individuals. #muslimban https://t.co/lDUfnbSLpn";
    tokenizer = tokenize(text);
    print(tokenizer)

mainTest()
