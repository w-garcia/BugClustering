from config import config as cfg
import util
import csv
from clustering_h_agglomerative import construct_matrix, build_ticket_list
from sklearn import neighbors
from sklearn.cluster import MiniBatchKMeans

# Perform clustering with sklearn library
def do_sklearn(system_name, prediction=None):
    class_clustering_filter = cfg.class_clustering_filter
    systems_filter = cfg.systems_filter

    if class_clustering_filter == 'none':
        cluster_by_all(system_name, prediction)
    else:
        cluster_by_filter(system_name, systems_filter, class_clustering_filter, prediction)


def cluster_by_all(system_name, prediction):
    vector_path = util.generate_meta_path(system_name, 'vectors')
    filename = vector_path + system_name + '_vectors.csv'

    # Last ticket is the ticket to predict
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        list_of_ticket_dicts = [rows for rows in reader]

    if len(list_of_ticket_dicts) < 1:
        print "[warning] : Not enough tickets to generate clusters. Skipping..."
        return

    # Create list of keyword weights, keeping string format
    list_of_weights = [ticket_dict['vector'] for ticket_dict in list_of_ticket_dicts]
    ticket_predict_weights = list_of_weights.pop().split(' ')

    # Construct matrix from the list of keyword dictionaries
    tickets_to_weights_matrix = construct_matrix(list_of_weights)

    if tickets_to_weights_matrix.shape[0] < 2:
        print "[warning] : Not enough tickets to generate clusters. Skipping..."
        return

    list_of_tickets = build_ticket_list(list_of_ticket_dicts)
    ticket_target_list = build_ticket_classes(list_of_tickets)

    if cfg.classification_method == 'knn':
        knn_classifier(prediction, ticket_predict_weights, ticket_target_list, tickets_to_weights_matrix)
    if cfg.classification_method == 'kmeans':
        kmeans_classifier(prediction, ticket_predict_weights, ticket_target_list, tickets_to_weights_matrix)


def knn_classifier(prediction, ticket_predict_weights, ticket_target_list, tickets_to_weights_matrix):
    knn = neighbors.KNeighborsClassifier()
    knn.fit(tickets_to_weights_matrix, ticket_target_list)
    predicted_class = knn.predict(ticket_predict_weights)[0]
    print "knn prediction: {}".format(predicted_class)
    if prediction is not None:
        prediction.append([predicted_class])


def kmeans_classifier(prediction, ticket_predict_weights, ticket_target_list, tickets_to_weights_matrix):
    kmeans = MiniBatchKMeans(n_clusters=len(ticket_target_list), init_size=len(tickets_to_weights_matrix) + 1)
    kmeans.fit(tickets_to_weights_matrix)

    predicted_class = kmeans.predict(ticket_predict_weights)[0]
    print "kmeans prediction: {}".format(ticket_target_list[predicted_class])
    if prediction is not None:
        prediction.append([ticket_target_list[predicted_class]])


def build_ticket_classes(list_of_tickets):
    target_list = []

    for ticket in list_of_tickets:
        for c in ticket.classes.split(' '):
            found_target = False
            for ci in cfg.classes_of_interest:
                if ci in c:
                    if len(cfg.classes_of_interest) > 1:
                        target_list.append(ci)
                    else: #only 1 given, add entire c
                        target_list.append(c)
                    found_target = True
                    break
            if found_target:
                break

    print "target list len {}".format(len(target_list))
    print "list of tickets len {}".format(len(list_of_tickets))

    return target_list


def cluster_by_filter(system_name, systems_filter, class_clustering_filter, prediction):
    print "knn.clustering_by_filter not implemented."
    pass
