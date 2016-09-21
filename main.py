from keyword_preprocess import process_system
from stemmer import stem_system
from low_freq_filter import low_freq_filter
from generate_vectors import generate_vectors
from clustering_h_agglomerative import do_h_agglomerative
from config import config as cfg
from jira import JIRA
from classifier import classify
from openstack_preprocess import process_openstack
from collections import defaultdict
import util
from analyzer import analyze
import numpy


def main():
    systems_filter = cfg.systems_filter
    perform_preprocessing = cfg.perform_preprocessing
    retrieve_labelling_datasets = cfg.retrieve_label_datasets

    # Fill local database with data from each system
    if perform_preprocessing:
        options = {'server': 'https://issues.apache.org/jira'}
        jira = JIRA(options=options)

        for system_name in util.systems:
            print "[status] : " + system_name + " pre-processing started."
            process_system(jira, system_name)
            stem_system(system_name)
            low_freq_filter(system_name)

    if retrieve_labelling_datasets:
        process_openstack()
        stem_system('openstack')
        low_freq_filter('openstack')

    # Perform clustering according to user specified granularity
    if cfg.clustering_mode == 'vanilla':
        print "[status] : vanilla clustering mode started."
        if systems_filter == 'none':
            generate_vectors("all_systems")
            do_h_agglomerative("all_systems")
        else:
            for system_name in util.systems:
                generate_vectors(system_name)
                do_h_agglomerative(system_name)
    elif cfg.clustering_mode == 'label':
        classify()
    else:
        print "[status] : {} clustering mode started with {} slice selecton.".format(cfg.clustering_mode, cfg.xvalidation_mode)
        # Perform cross validation based on config: either k-fold or random sub-sampling
        if cfg.xvalidation_mode == 'kfold':
            class_to_scores_dict = defaultdict(dict)
            for c in cfg.classes_of_interest:
                class_to_scores_dict[c]['recalls'] = []
                class_to_scores_dict[c]['precisions'] = []
                class_to_scores_dict[c]['f_scores'] = []

            for i in range(int(1 / cfg.test_dataset_split)):
                print "[kfold] : Classifying slice {}".format(i)
                classify(slice=i)
                scores_dict = analyze(return_accuracies=True)
                for c in scores_dict:
                    class_to_scores_dict[c]['recalls'].append(scores_dict[c]['recall'])
                    class_to_scores_dict[c]['precisions'].append(scores_dict[c]['precision'])
                    class_to_scores_dict[c]['f_scores'].append(scores_dict[c]['f1'])

            print "RESULTS OF {}; {} on {}".format(cfg.classification_method, cfg.model_selection, cfg.test_dataset)
            for c in class_to_scores_dict:
                avg_recall = sum(class_to_scores_dict[c]['recalls']) / len(class_to_scores_dict[c]['recalls'])
                recall_std = numpy.std(class_to_scores_dict[c]['recalls'])

                avg_precision = sum(class_to_scores_dict[c]['precisions']) / len(class_to_scores_dict[c]['precisions'])
                precision_std = numpy.std(class_to_scores_dict[c]['precisions'])

                avg_f_score = sum(class_to_scores_dict[c]['f_scores'])/len(class_to_scores_dict[c]['f_scores'])
                f_score_std = numpy.std(class_to_scores_dict[c]['f_scores'])

                print "{}: Recall: {}+-{}; Precision: {}+-{}; F1: {}+-{};".format(c,
                                                                                  format(avg_recall, '.3f'),
                                                                                  format(recall_std, '.3f'),
                                                                                  format(avg_precision, '.3f'),
                                                                                  format(precision_std, '.3f'),
                                                                                  format(avg_f_score, '.3f'),
                                                                                  format(f_score_std, '.3f'))

        elif cfg.xvalidation_mode == 'rand_ss':
            classify()
            analyze()

if __name__ == '__main__':
    main()
