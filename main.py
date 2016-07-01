from keyword_preprocess import process_system
from stemmer import stem_system
from low_freq_filter import low_freq_filter
from generate_vectors import generate_vectors
from clustering import cluster
from jira import JIRA
import util
import sys

def main():
    #input_proc = raw_input("This will over-write system databases. Proceed? ").lower()
    #input_proc = 'y'
    #if input_proc != 'y':
    #    return

    options = {'server': 'https://issues.apache.org/jira'}
    #jira = JIRA(options=options)

    if len(sys.argv) < 4:
        print "[Error] : Incorrect Usage\n"
        print "Usage: python main.py <cluster_by_class (True/False)> <cluster_by_system (True/False)> <by_class_mode (all/system/both)>"
        return

    by_class_option = sys.argv[1].lower()
    by_system_option = sys.argv[2].lower()
    by_class_mode = sys.argv[3].lower()

    for system_name in util.systems:
        print "[status] : " + system_name + " pre-processing started."

        #process_system(jira, system_name)
        #stem_system(system_name)
        #low_freq_filter(system_name)

    if by_class_option == 'true':
        print "[status] : By-class clustering started."

        if by_class_mode == 'all' or by_class_mode == 'both':
            generate_vectors('all_systems', by_classes=True, by_class_mode='all')
            cluster('all_systems', by_classes=True, by_class_mode='all')

        if by_class_mode == 'system' or by_class_mode == 'both':
            for system_name in util.systems:
                generate_vectors(system_name, by_classes=True, by_class_mode='system')
                cluster(system_name, by_classes=True, by_class_mode='system')

    if by_system_option == 'true':
        for system_name in util.systems:
            print "[status] : " + system_name + " clustering started."

            generate_vectors(system_name, by_system=True)
            cluster(system_name, by_system=True)


if __name__ == '__main__':
    main()
