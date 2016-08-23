import util
from config import config as cfg
import csv


def analyze(return_accuracies=False):
    cls_path = util.generate_meta_path(cfg.model_selection, 'classifier')
    util.ensure_path_exists(cls_path)
    filename = cls_path + cfg.test_dataset + '_classifier.csv'

    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        list_of_ticket_dicts = [rows for rows in reader]

    list_statistics = generate_statistics(list_of_ticket_dicts)

    filename = cls_path + cfg.test_dataset + '_statistics.csv'
    write_statistics_file(filename, list_statistics)

    if return_accuracies:
        final_dict = list_statistics[len(list_statistics) - 1]
        return final_dict['category score'], final_dict['class score']


def generate_statistics(list_of_dicts):
    _list_truths = [row['ground truth'] for row in list_of_dicts]
    _list_predictions = [row['prediction'] for row in list_of_dicts]
    _list_descriptions = [row['description'] for row in list_of_dicts]

    _total_category_accuracy = 0.0
    _total_class_accuracy = 0.0
    _total_class_predictions = 0
    _list_desc_length_to_score = []

    n = len(list_of_dicts)

    for i in range(len(list_of_dicts)):

        _truths = set(_list_truths[i].split(' '))
        _predictions = set(_list_predictions[i].split(' '))

        _truth_categories = set()
        _truths_of_interest = set()

        _prediction_categories = set()
        _predictions_of_interest = set()

        # First, fill in the class categories of interest from config in the truth list
        for ci in cfg.classes_of_interest:
            for truth in _truths:
                if ci in truth:
                    _truth_categories.add(ci)
                    _truths_of_interest.add(truth)

            for prediction in _predictions:
                if ci in prediction:
                    _prediction_categories.add(ci)
                    if len(prediction) > 3:
                        _predictions_of_interest.add(prediction)

        print "[analysis] : Truth categories for ticket {}: {}".format(i, _truth_categories)
        print "           : Truths of interest: {}".format(_truths_of_interest)
        print "           : Prediction categories: {}".format(_prediction_categories)
        print "           : Predictions of interest: {}".format(_predictions_of_interest)

        # This ticket had no classes of interest
        if len(_truth_categories) == 0:
            # If a guess was made, this detracts from the accuracy, so keep n the same and continue
            if _prediction_categories:
                continue
            #TODO: Need to modify vector generator so tickets without classes of interest aren't included in clustering.
            # If a prediction wasn't made, that' good. Subtract 1 from n because this ticket wasn't useful.
            n -= 1
            continue

        # Compare across categories
        _category_intersect = set.intersection(_truth_categories, _prediction_categories)
        category_score = float(len(_category_intersect)) / float(len(_truth_categories))
        _total_category_accuracy += category_score

        class_score = 'nil'
        # There are predictions of interest, so it tried to guess specific classes for this ticket
        if _predictions_of_interest:
            _total_class_predictions += 1
            _prediction_intersect = set.intersection(_truths_of_interest, _predictions_of_interest)
            class_score = float(len(_prediction_intersect)) / float(len(_truths_of_interest))
            _total_class_accuracy += class_score
            print _prediction_intersect
            print class_score

        _temp_dict = {'description length': len(_list_descriptions[i].split(' ')),
                      'description': _list_descriptions[i],
                      'category score': category_score,
                      'class score': class_score}

        _list_desc_length_to_score.append(_temp_dict)

    if _total_class_predictions != 0:
        class_accuracy = float(_total_class_accuracy / _total_class_predictions)
    else:
        class_accuracy = 'nil'

    category_accuracy = float(_total_category_accuracy / n)
    print "[results] : Category accuracy: {}".format(category_accuracy)
    print "          : Class accuracy: {}".format(class_accuracy)

    _final_dict = {'description length': '-----',
                   'description': 'final averages -----',
                   'category score': category_accuracy,
                   'class score': class_accuracy}
    _list_desc_length_to_score.append(_final_dict)

    return _list_desc_length_to_score


def write_statistics_file(filename, list_dicts):
    with open(filename, 'w') as csvfile:
        fieldnames = list_dicts[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in list_dicts:
            writer.writerow(row)