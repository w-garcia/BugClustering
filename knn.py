from config import config as cfg
import util
import csv
from h_agglomerative import construct_matrix, build_ticket_list
from sklearn import neighbors

# Perform K-Nearest Neighbor clustering
def knn_clustering(system_name, prediction=None):
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

    # Construct matrix from the list of keyword dictionaries
    tickets_to_weights_matrix = construct_matrix(list_of_weights)

    if tickets_to_weights_matrix.shape[0] < 2:
        print "[warning] : Not enough tickets to generate clusters. Skipping..."
        return

    list_of_tickets = build_ticket_list(list_of_ticket_dicts)

    ticket_to_predict_weights = tickets_to_weights_matrix.pop()

    knn = neighbors.KNeighborsClassifier()
    knn.fit(tickets_to_weights_matrix, ticket_to_predict_weights)
    knn.predict(ticket_to_predict_weights)


def cluster_by_filter(system_name, systems_filter, class_clustering_filter, prediction):
    print "knn.clustering_by_filter not implemented."
    pass
