import nltk
import collections
from peewee import *


def low_freq_filter(db):
    class Stemmed_Keywords(Model):
        description = TextField()
        classification = CharField()

        class Meta:
            database = db

    class LFF_Keywords(Stemmed_Keywords):
        pass

    word_to_count_dict = collections.Counter()

    for row in Stemmed_Keywords.select():
        # Columns: row.description, row.classification
        words = nltk.word_tokenize(row.description)
        for word in words:
            word_to_count_dict[word] += 1

    list_of_lff_dicts = []

    for row in Stemmed_Keywords.select():
        words_to_keep = []
        words = nltk.word_tokenize(row.description)
        for word in words:
            if word_to_count_dict[word] != 1:
                words_to_keep.append(word)
        list_of_lff_dicts.append({'description': u' '.join(words_to_keep), 'classification': row.classification})

    LFF_Keywords.create_table()

    with db.atomic():
        LFF_Keywords.insert_many(list_of_lff_dicts).execute()

    print "Stripped " + str(db.database) + " of low frequency words."

