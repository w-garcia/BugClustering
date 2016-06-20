from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import util
import nltk
import os
import string
from peewee import *

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

    for row in Terse_PreProcessed_Keywords.select():
        stripped_description = util.strip_autogen_info(row.description)
        words = nltk.word_tokenize(stripped_description)

        # Keeps nouns and verbs
        words_to_keep = []
        word_to_pos_pair_list = nltk.pos_tag(words)
        for word, tag in word_to_pos_pair_list:
            #if word in stopwords.words('english'):
            if 'N' in tag or 'V' in tag:
                #words.remove(word)
                words_to_keep.append(word)

        stems = create_stem_list(words_to_keep)

        list_of_stem_dicts.append({'description': u' '.join(stems).encode('utf-8'),
                                   'classification': row.classification})

    with db.atomic():
        Stemmed_Keywords.insert_many(list_of_stem_dicts).execute()

    print "Stemmed " + str(db.database) + "."


def create_stem_list(words):
    stems = []
    porter_stemmer = PorterStemmer()
    for word in words:
        if word in string.punctuation:
            words.remove(word)
        else:
            stems.append(porter_stemmer.stem(word))
    return stems



