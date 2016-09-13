from nltk.corpus import stopwords, wordnet as wn
from nltk.stem import PorterStemmer, WordNetLemmatizer
import DBModel
import util
import nltk
import os
import re
from config import config as cfg
cwd = os.getcwd()


def stem_system(system_name):
    list_of_stem_dicts = []
    banned_words = []

    print "[stemmer] Stemming {}.".format(system_name)
    porter_stemmer = PorterStemmer()
    wordnet_lemmatizer = WordNetLemmatizer()
    vocab = set()

    if cfg.clustering_mode == 'label':
        temp_list = [row for row in DBModel.Terse_PreProcessed_Keyword.get_db_ref_by_system(cfg.labelling_dataset).random(cfg.labelling_dataset)]
        selection = []
        for row in temp_list:
            if row.status != 'New' and row.status != 'Expired' and row.status != 'In Progress':
                selection.append(row)

    else:
        selection = DBModel.Terse_PreProcessed_Keyword.get_db_ref_by_system(system_name).select()

    for row in selection:
        if cfg.clustering_mode == 'label' and len(list_of_stem_dicts) == 1000:
            break

        stripped_description = util.strip_autogen_info(row.description)

        stems = []
        sentences = nltk.sent_tokenize(stripped_description)

        # Tokenize into sentences first for better POS tagging
        for sentence in sentences:
            words = nltk.word_tokenize(sentence)

            regex_proc_words = []
            #print "Words:"
            #print words
            #print '\n'

            # Handle special cases of words with symbols and capitals, while preserving capitalization and order.
            for word in words:
                word = re.sub(r'\d+', '', word)
                word = word.replace(system_name, '')

                if not re.match('[A-Za-z]', word):
                    continue

                split_word_list = regex_match_reduce(word)

                if len(split_word_list) > 0:
                    for split_word in split_word_list:
                        regex_proc_words.append(split_word)
                else:
                    regex_proc_words.append(word)

            #print "Regex proc words:"
            #print regex_proc_words
            #print '\n'

            # Keeps nouns and verbs
            word_to_pos_pair_list = nltk.pos_tag(regex_proc_words)

            for word, tag in word_to_pos_pair_list:
                if word in stopwords.words('english'):
                    continue
                if len(word) < 3:
                    continue
                if '\'' in word:
                    continue
                word = word.lower()

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

        if len(stems) <= 4:
            continue

        if cfg.clustering_mode == 'label':
            list_of_stem_dicts.append({'system': system_name,
                                       'description': u' '.join(stems).encode('utf-8'),
                                       'classification': row.classification,
                                       'title': row.title,
                                       'status': row.status,
                                       'issue_number': row.issue_number,
                                       'target': row.target})
        else:
            list_of_stem_dicts.append({'system': system_name,
                                       'description': u' '.join(stems).encode('utf-8'),
                                       'classification': row.classification})

    DBModel.Stemmed_Keyword.get_db_ref_by_system(system_name).overwrite_system_rows(system_name, list_of_stem_dicts)

    print "[stemmer] : Stemmed " + system_name + "."


def regex_match_reduce(word):
    master_regex = re.compile(r'[A-Z]*[a-z]+')
    if len(master_regex.findall(word)):
        return master_regex.findall(word)

    return []


def find_system_synonym_from_stem(s1):
    sys_synonyms = {'oom': 'outofmemory', 'tdd': 'testdrivendevelopment',
                    'hdf': 'hdfs', 'except': 'exception', 'flum': 'flume', 'lifecyc': 'lifecycle',
                    'interfac': 'interface', 'improv': 'improve', 'stabl': 'stable', 'cach': 'cache', 'nod': 'node',
                    'npe': 'exception', 'mapred': 'mapreduce', 'zoo': 'zookeeper', 'hfile': 'file',
                    'cfg': 'config', 'mapr': 'mapreduce', 'synchron': 'sync', 'err': 'error', 'holder': 'hold',
                    'agre': 'agree', 'algo': 'algorithm', 'amoun': 'amount', 'analyz': 'analysi', 'assig': 'assign',
                    'branc': 'branch', 'broken': 'break', 'buf': 'buffer', 'callabl': 'call', 'additiv': 'add',
                    'dir': 'directori', 'increas': 'increment', 'indic': 'index', 'integr': 'integrate', 'int': 'integ',
                    'lose': 'loss', 'mini': 'min', 'partit': 'partition', 'multi': 'multipl', 'regress': 'regression',
                    'replic': 'replica', 'secondari': 'second', 'startup': 'start', 'statu': 'state', 'storag': 'store',
                    'transact': 'transfer', 'translat': 'transfer', 'verifi': 'verif', 'shut': 'shutdown', 'mem': 'memori'}
    if s1 in sys_synonyms.keys():
        return sys_synonyms[s1]
    return s1


def reduce_according_to_phrase(w1):
    phrases_to_filter = ['outofmemory', 'zip', 'lifecyc', 'stabl', 'batch',
                         'properti', 'recov', 'mapred', 'yarn', 'runtim',
                         'heartbeat', 'stress', 'hadoop', 'buffer', 'agre',
                         'cassandra', 'filesystem', 'ttl', 'drop', 'wait', 'visit', 'accumul', 'admin',
                         'assign', 'amoun', 'directori', 'system', 'job', 'launch', 'sink', 'block']
    for phrase in phrases_to_filter:
        if phrase in w1:
            #print phrase
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
