from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
import util
import nltk
import os
import string
from peewee import *
import re

cwd = os.getcwd()


def stem_system(db):
    class Full_PreProcessed_Keywords(Model):
        description = TextField()
        classification = CharField()

        class Meta:
            database = db

    class Terse_PreProcessed_Keywords(Full_PreProcessed_Keywords):
        pass

    class Stemmed_Keywords(Full_PreProcessed_Keywords):
        pass

    Stemmed_Keywords.create_table()

    list_of_stem_dicts = []
    banned_words = ['is', 'and', 'etc', 'with', 'of', 'in', 'that', 'on', 'do', 'wo' 'ca', 'are', 'get', 'from',
                    'for', 'at', 'if', 'be', 'use', 'have', 'does', 'take', 'has', 'as', 'after', 'before', 'by',
                    'row', 'column', 'am', 'nn', 'go', 'behavior']

    porter_stemmer = PorterStemmer()
    wordnet_lemmatizer = WordNetLemmatizer()
    for row in Terse_PreProcessed_Keywords.select():
    #for row in Full_PreProcessed_Keywords.select():
        stripped_description = util.strip_autogen_info(row.description)
        words = nltk.word_tokenize(stripped_description)

        # Keeps nouns and verbs
        stems = []
        word_to_pos_pair_list = nltk.pos_tag(words)

        for word, tag in word_to_pos_pair_list:
            word = re.sub(r'\d+', '', word).lower()
            word = word.replace(str(db.database), '')
            if (word not in stopwords.words('english')) and len(word) > 3 and re.match('[a-z0-9]', word) and not ('\'' in word):
                if 'V' in tag:
                    word = wordnet_lemmatizer.lemmatize(word, pos='v')
                    stem = porter_stemmer.stem(word)
                    if stem not in banned_words:
                        stems.append(stem)
                elif 'NN' in tag:
                    word = wordnet_lemmatizer.lemmatize(word)
                    stem = porter_stemmer.stem(word)
                    stems.append(stem)
                    if stem not in banned_words:
                        stems.append(stem)

        #stems = create_stem_list(words_to_keep)

        list_of_stem_dicts.append({'description': u' '.join(stems).encode('utf-8'),
                                   'classification': row.classification})

    with db.atomic():
        Stemmed_Keywords.insert_many(list_of_stem_dicts).execute()

    print "Stemmed " + str(db.database) + "."


