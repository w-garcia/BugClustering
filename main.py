from keyword_preprocess import process_system
from stemmer import stem_system
from low_freq_filter import low_freq_filter
from generate_vectors import generate_vectors
from clustering import cluster
from jira import JIRA
import util


def main():
    #input_proc = raw_input("This will over-write system databases. Proceed? ").lower()
    #input_proc = 'y'
    #if input_proc != 'y':
    #    return

    options = {'server': 'https://issues.apache.org/jira'}
    #jira = JIRA(options=options)

    for system_name in util.systems:
        print "[status] : " + system_name + " started."

        #process_system(jira, system_name)
        #stem_system(system_name)
        #low_freq_filter(system_name)
        #generate_vectors(system_name, by_classes=True, by_system=False, class_key="a-")
        cluster(system_name, by_classes=True, by_system=False, class_key="a-")


if __name__ == '__main__':
    main()
