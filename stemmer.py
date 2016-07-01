from nltk.corpus import stopwords, wordnet as wn
from nltk.stem import PorterStemmer, WordNetLemmatizer
import DBModel
import util
import nltk
import os
import re

cwd = os.getcwd()


def stem_system(system_name):
    list_of_stem_dicts = []
    banned_words = ['is', 'and', 'etc', 'with', 'of', 'in', 'that', 'on', 'do', 'wo' 'ca', 'are', 'get', 'from',
                    'for', 'at', 'if', 'be', 'use', 'have', 'does', 'take', 'has', 'as', 'after', 'before', 'by',
                    'caus', 'row', 'column', 'am', 'nn', 'go', 'consid', 'turn', 'bring', 'ack', 'us', 'today', 'hour',
                    'take', 'log', 'need', 'with', 'becom', 'though', 'with', 'date', 'upon', 'come', 'came', 'behavior',
                    'around', 'henc', 'hyphen', 'think', 'unless', 'want', 'way', 'syslog', 'logj', 'dy', 'enabl', 'see',
                    'mechan', 'retri', 'roll', 'run', 'other', 'tri', 'call', 'make', 'seem', 'avro', 'http', 'million',
                    'hundred', 'look', 'leav', 'guarante', 'line', 'merkl', 'propos', 'decid', ':', 'let']

    porter_stemmer = PorterStemmer()
    wordnet_lemmatizer = WordNetLemmatizer()
    vocab = set()

    for row in DBModel.Terse_PreProcessed_Keyword.select_by_system(system_name):
    #for row in Full_PreProcessed_Keywords.select():
        stripped_description = util.strip_autogen_info(row.description)
        #stripped_description = util.strip_autogen_to_eol(row.description)
        words = nltk.word_tokenize(stripped_description)

        # Keeps nouns and verbs
        stems = []
        word_to_pos_pair_list = nltk.pos_tag(words)

        for word, tag in word_to_pos_pair_list:
            word = re.sub(r'\d+', '', word).lower()
            word = word.replace(system_name, '')
            if (word not in stopwords.words('english')) and len(word) > 3 and re.match('[a-z0-9]', word) and not ('\'' in word):

                if 'V' in tag:
                    word = wordnet_lemmatizer.lemmatize(word, pos='v')
                    word = reduce_according_to_phrase(word)
                    word = get_most_likely_synonym(word, vocab, 'v')

                    stem = porter_stemmer.stem(word)
                    stem = find_system_synonym_from_stem(stem)

                    if stem not in banned_words and len(stem) > 2:
                        stems.append(stem)

                elif 'NN' in tag:
                    word = wordnet_lemmatizer.lemmatize(word)
                    word = reduce_according_to_phrase(word)
                    word = get_most_likely_synonym(word, vocab, 'n')

                    stem = porter_stemmer.stem(word)
                    stem = find_system_synonym_from_stem(stem)

                    if stem not in banned_words and len(stem) > 2:
                        stems.append(stem)

        #stems = create_stem_list(words_to_keep)

        list_of_stem_dicts.append({'system': system_name,
                                   'description': u' '.join(stems).encode('utf-8'),
                                   'classification': row.classification})

    DBModel.Stemmed_Keyword.overwrite_system_rows(system_name, list_of_stem_dicts)

    print "[Stemmer] : Stemmed " + system_name + "."


def find_system_synonym_from_stem(s1):
    sys_synonyms = {'oom': 'outofmemory', 'tdd': 'testdrivendevelopment',
                    'hdf': 'hdfs', 'except': 'exception', 'flum': 'flume', 'lifecyc': 'lifecycle',
                    'interfac': 'interface', 'improv': 'improve', 'stabl': 'stable', 'cach': 'cache', 'nod': 'node',
                    'npe': 'nullpointerexception'}
    if s1 in sys_synonyms.keys():
        return sys_synonyms[s1]
    return s1


def reduce_according_to_phrase(w1):
    phrases_to_filter = ['sourc', 'except', 'outofmemory', 'sink', 'hdfs', 'zip', 'lifecyc', 'block', 'stabl',
                         'batch', 'properti', 'node', 'recov', 'creat', 'config']
    for phrase in phrases_to_filter:
        if phrase in w1:
            return phrase
    return w1


def get_most_likely_synonym(w1, vocabulary, pos):
    if w1 not in vocabulary:
        synonyms = [x.name().split('.')[0] for x in wn.synsets(w1) if x.name().split('.')[1] == pos]
        if len(synonyms) > 0:
            for likely_word in synonyms:
                if likely_word in vocabulary:
                    return likely_word
        # Cache word into vocabulary
        vocabulary.add(w1)
    return w1
