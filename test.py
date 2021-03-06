"""
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import string
import nltk
from nltk.corpus import wordnet as wn
"""
import re

contractions = {
"ain't": "am not; are not; is not; has not; have not",
"aren't": "are not; am not",
"can't": "cannot",
"can't've": "cannot have",
"'cause": "because",
"could've": "could have",
"couldn't": "could not",
"couldn't've": "could not have",
"didn't": "did not",
"doesn't": "does not",
"don't": "do not",
"hadn't": "had not",
"hadn't've": "had not have",
"hasn't": "has not",
"haven't": "have not",
"he'd": "he had / he would",
"he'd've": "he would have",
"he'll": "he shall / he will",
"he'll've": "he shall have / he will have",
"he's": "he has / he is",
"how'd": "how did",
"how'd'y": "how do you",
"how'll": "how will",
"how's": "how has / how is / how does",
"I'd": "I had / I would",
"I'd've": "I would have",
"I'll": "I shall / I will",
"I'll've": "I shall have / I will have",
"I'm": "I am",
"I've": "I have",
"isn't": "is not",
"it'd": "it had / it would",
"it'd've": "it would have",
"it'll": "it shall / it will",
"it'll've": "it shall have / it will have",
"it's": "it has / it is",
"let's": "let us",
"ma'am": "madam",
"mayn't": "may not",
"might've": "might have",
"mightn't": "might not",
"mightn't've": "might not have",
"must've": "must have",
"mustn't": "must not",
"mustn't've": "must not have",
"needn't": "need not",
"needn't've": "need not have",
"o'clock": "of the clock",
"oughtn't": "ought not",
"oughtn't've": "ought not have",
"shan't": "shall not",
"sha'n't": "shall not",
"shan't've": "shall not have",
"she'd": "she had / she would",
"she'd've": "she would have",
"she'll": "she shall / she will",
"she'll've": "she shall have / she will have",
"she's": "she has / she is",
"should've": "should have",
"shouldn't": "should not",
"shouldn't've": "should not have",
"so've": "so have",
"so's": "so as / so is",
"that'd": "that would / that had",
"that'd've": "that would have",
"that's": "that has / that is",
"there'd": "there had / there would",
"there'd've": "there would have",
"there's": "there has / there is",
"they'd": "they had / they would",
"they'd've": "they would have",
"they'll": "they shall / they will",
"they'll've": "they shall have / they will have",
"they're": "they are",
"they've": "they have",
"to've": "to have",
"wasn't": "was not",
"we'd": "we had / we would",
"we'd've": "we would have",
"we'll": "we will",
"we'll've": "we will have",
"we're": "we are",
"we've": "we have",
"weren't": "were not",
"what'll": "what shall / what will",
"what'll've": "what shall have / what will have",
"what're": "what are",
"what's": "what has / what is",
"what've": "what have",
"when's": "when has / when is",
"when've": "when have",
"where'd": "where did",
"where's": "where has / where is",
"where've": "where have",
"who'll": "who will",
"who'll've": "who will have",
"who's": "who is",
"who've": "who have",
"why's": "why is",
"why've": "why have",
"will've": "will have",
"won't": "will not",
"won't've": "will not have",
"would've": "would have",
"wouldn't": "would not",
"wouldn't've": "would not have",
"y'all": "you all",
"y'all'd": "you all would",
"y'all'd've": "you all would have",
"y'all're": "you all are",
"y'all've": "you all have",
"you'd": "you had",
"you'd've": "you would have",
"you'll": "you shall",
"you'll've": "you shall have",
"you're": "you are",
"you've": "you have"
}
"""
# http://sujitpal.blogspot.com/2013/02/checking-for-word-equivalence-using.html
def similarity(word1, word2, sim=wn.path_similarity):
    synsets1 = wn.synsets(word1)
    synsets2 = wn.synsets(word2)
    sim_scores = []

    for synset1 in synsets1:
        for synset2 in synsets2:
            sim_scores.append(sim(synset1, synset2))

    if len(sim_scores) == 0:
        return 0
    else:
        return max(sim_scores)


def create_stem_list(words):
    stems = []
    porter_stemmer = PorterStemmer()
    for word in words:
        if re.match('[a-z0-9]', word) and not ('\'' in word): #word in string.punctuation or
            stems.append(porter_stemmer.stem(word))
    return stems


def tokenize(text):
    #text = "".join([ch for ch in text if ch not in string.punctuation])
    tokens = nltk.word_tokenize(text)
    word_to_pos_pair_list = nltk.pos_tag(tokens)

    print word_to_pos_pair_list
    stems = create_stem_list(tokens)
    return stems

    dots = re.compile(r'([a-z]+\.+[a-z]+)')
    if len(dots.findall(word)):
        return [x for x in word.split('.') if len(x) >= 3]

    hypens = re.compile(r'[a-z]+\-+[a-z]+')
    if len(hypens.findall(word)):
        return [x for x in word.split('-') if len(x) >= 3]

    fslashes = re.compile(r'[a-z]+/+[a-z]+')
    if len(fslashes.findall(word)):
        return [x for x in word.split('/') if len(x) >= 3]

    bslashes = re.compile(r'[a-z]+\\+[a-z]+')
    if len(bslashes.findall(word)):
        return [x for x in word.split('\\') if len(x) >= 3]

    uscores = re.compile(r'[a-z]+_+[a-z]+')
    if len(uscores.findall(word)):
        return [x for x in word.split('_') if len(x) >= 3]

"""
text = "ta_too_many_fetch_failur=true"
print re.findall(r'[A-Z]*[a-z]+', text)

#print tokenize(text.lower())
#syns = [x for x in wn.synsets("agreement") if x.name().split('.')[1] == 'n']
#syns = wn.synsets("take")
