import os
import errno
import numpy
import math
#TODO: Create string constants file for directories and filenames

#TODO: move to string constants file
systems = ['cassandra', 'flume', 'hbase', 'hdfs', 'mapreduce', 'zookeeper']
cwd = os.getcwd()


# http://stackoverflow.com/questions/273192/how-to-check-if-a-directory-exists-and-create-it-if-necessary
def ensure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def strip_autogen_info(line):
    begin_key = line.find(']') + 2
    end_key = line.find('\n') - 2
    # TODO: regex might be more efficient
    # remove stop words
    """
    word_list = nltk.word_tokenize(useful_description)
    for word in word_list:
        if word in stopwords.words('english'):
            word_list.remove(word)
    """
    return line[begin_key:end_key + 1]


def combine():
    f = open(cwd + '/kw/my_data.txt', 'w')

    for system_name in systems:
        fw = open(cwd + '/kw/' + system_name + '_kw.txt', 'r')
        for line in fw:
            f.write(line)
    print "Combined files."


def create_similarity_matrix(db, list_of_keyword_vectors):
    similarity_matrix = numpy.zeros((len(list_of_keyword_vectors), len(list_of_keyword_vectors)))

    for i in range(len(similarity_matrix)):
        for j in range(i):
            x = euclidian(list_of_keyword_vectors[i], list_of_keyword_vectors[j])
            similarity_matrix[i, j] = x
            similarity_matrix[j, i] = x
            print("{}, {}".format(i, j))

    numpy.savetxt("{}_similarity_matrix.csv".format(db.database), similarity_matrix, delimiter=",")
    return similarity_matrix


def load_similarity_matrix(db):
    return numpy.genfromtxt("{}_similarity_matrix.csv".format(db.database), delimiter=',')


def euclidian(vector_i, vector_j):
    result = 0

    for word in vector_i.keys():
        result += abs(int(vector_j[word]) - int(vector_i[word]))**2

    result = math.sqrt(result)
    return result