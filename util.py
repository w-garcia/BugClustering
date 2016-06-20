import os
import errno

#TODO: Create string constants file for directories and filenames

#TODO: move to string constants file
systems = ['zookeeper']#['cassandra', 'flume', 'hbase', 'hdfs', 'mapreduce', 'zookeeper']
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
    # TODO: look for parts of speech first and preserve?
    # TODO: remove punctuation
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