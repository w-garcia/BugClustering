import util
from config import config as cfg
import csv
from collections import defaultdict


def analyze(return_accuracies=False):
    cls_path = util.generate_meta_path(cfg.model_selection, 'classifier')
    util.ensure_path_exists(cls_path)

    classifier_filename = ''
    stats_filename = ''

    if cfg.classification_method == 'default':
        classifier_filename = cls_path + cfg.test_dataset + '_classifier.csv'
        stats_filename = cls_path + cfg.test_dataset + '_statistics.csv'
    elif cfg.classification_method == 'knn':
        classifier_filename = cls_path + cfg.test_dataset + '_knn_classifier.csv'
        stats_filename = cls_path + cfg.test_dataset + '_knn_statistics.csv'
    elif cfg.classification_method == 'kmeans':
        classifier_filename = cls_path + cfg.test_dataset + '_kmeans_classifier.csv'
        stats_filename = cls_path + cfg.test_dataset + '_kmeans_statistics.csv'

    with open(classifier_filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        list_of_ticket_dicts = [rows for rows in reader]

    scores_dict = generate_statistics(list_of_ticket_dicts)
    #write_statistics_file(stats_filename, list_statistics)

    if return_accuracies:
        return scores_dict


def generate_statistics(list_of_dicts):
    _list_truths = [row['ground truth'] for row in list_of_dicts]
    _list_predictions = [row['prediction'] for row in list_of_dicts]
    _list_descriptions = [row['description'] for row in list_of_dicts]

    # Build confusion matrix template.
    # predictions x actuals. Row n+1 is used for total actuals,
    # and column n+1 is used for total predictions
    confusion_matrix = defaultdict(dict)
    for actual in cfg.classes_of_interest:
        for predicted in cfg.classes_of_interest:
            confusion_matrix[actual][predicted] = 0.0

    _list_desc_length_to_score = []

    n = len(list_of_dicts)
    for i in range(n):
        _truth = extract_truth(set(_list_truths[i].split(' ')))
        _prediction = set(_list_predictions[i].split(' ')).pop()

        confusion_matrix[_truth][_prediction] += 1.0

        _temp_dict = {'description length': len(_list_descriptions[i].split(' ')),
                      'description': _list_descriptions[i],
                      'precision': '',
                      'recall': '',
                      'f-score': ''}

        _list_desc_length_to_score.append(_temp_dict)

    total_actuals_dict = defaultdict(int)
    total_predictions_dict = defaultdict(int)
    for actual in cfg.classes_of_interest:
        for prediction in cfg.classes_of_interest:
            total_predictions_dict[prediction] += confusion_matrix[actual][prediction]
            total_actuals_dict[actual] += confusion_matrix[actual][prediction]

    scores = defaultdict(dict)
    for c in cfg.classes_of_interest:
        scores[c]['recall'] = 1.0
        scores[c]['precision'] = 1.0
        if total_actuals_dict[c] != 0.0:
            scores[c]['recall'] = confusion_matrix[c][c] / total_actuals_dict[c]
        if total_predictions_dict[c] != 0.0:
            scores[c]['precision'] = confusion_matrix[c][c] / total_predictions_dict[c]
        precision = scores[c]['precision']
        recall = scores[c]['recall']
        scores[c]['f1'] = 0.0
        if precision != 0 and recall != 0:
            scores[c]['f1'] = float((2*precision*recall) / (precision + recall))

    print_confusion_matrix(confusion_matrix, total_actuals_dict, total_predictions_dict)

    print "[analyzer] : Scores:"
    for c in scores:
        print "{}: Precision: {}, Recall: {}, F1: {}".format(c, scores[c]['precision'], scores[c]['recall'],
                                                             scores[c]['f1'])

    return scores


def print_confusion_matrix(confusion_matrix, total_actuals_dict, total_predictions_dict):
    print "[analyzer] : Here is the confusion matrix:"
    for c in confusion_matrix:
        strin = ""
        for ci in confusion_matrix[c]:
            strin += "{} ".format(confusion_matrix[c][ci])
        strin += str(total_actuals_dict[c])
        print strin
    last_row = ""
    for c in total_predictions_dict:
        last_row += "{} ".format(total_predictions_dict[c])
    print last_row


def extract_truth(truths_set):
    for truth in truths_set:
            for c in cfg.classes_of_interest:
                if c in truth:
                    return c
    raise ValueError('Class of interest not found in bug\'s ground truth.')


def write_statistics_file(filename, list_dicts):
    with open(filename, 'w') as csvfile:
        fieldnames = list_dicts[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in list_dicts:
            writer.writerow(row)
