import nltk
import csv
import numpy
import math
from matplotlib import pyplot
from scipy.cluster.hierarchy import *#dendrogram, linkage, cophenet
from scipy.spatial.distance import pdist
from peewee import *
import copy


class LabelledClusterNode(ClusterNode):
    """
    Custom ClusterNode class for use in binary or n-ary trees.
    """
    def __init__(self, cn):
        ClusterNode.__init__(self, cn.get_id(), cn.get_left(), cn.get_right(), 0)
        self.label = None
        self.parent = None
        self.children_list = []
        self.head = None


class LabelledBT:
    def __init__(self, root, list_of_keyword_to_weights):
        self.binary_tree = LabelledClusterNode(root)
        self.list_of_keyword_to_weights = list_of_keyword_to_weights

    def generate_keywords_label(self, nid):
        trouble_ticket = self.list_of_keyword_to_weights[nid]
        nonzero_keywords = []
        for keyword in trouble_ticket.keys():
            if int(trouble_ticket[keyword]) > 0:
                nonzero_keywords.append(keyword)
        return nonzero_keywords

    def create_label_tree(self):
        # DFS through BT and label leaf nodes according to T
        stack = [self.binary_tree]
        parents = []
        while stack:
            node = stack.pop()
            nid = node.get_id()

            # This checks if left is None
            if node.is_leaf():
                node.label = self.generate_keywords_label(nid)
                print node.label
            else:
                stack.append(node.get_left())
                node.get_left().parent = node
                parents.append(node)

            if node.get_right() is not None:
                stack.append(node.get_right())
                node.get_right().parent = node

        # Now go to each non-leaf node and label as intersection of all leaf nodes below it
        i = len(parents) - 1
        while i >= 0:
            right_child = parents[i].get_right()
            left_child = parents[i].get_left()
            if right_child is None:
                parents[i].label = left_child.label
            else:
                intersection = set.intersection(set(left_child.label), set(right_child.label))
                if not intersection:
                    parents[i].label = ['unknown']
                else:
                    parents[i].label = list(intersection)
            i -= 1
        """
        stack = [self.binary_tree]
        while stack:
            node = stack.pop()
            print node.label
            if node.get_left() is not None:
                stack.append(node.get_left())
            if node.get_right() is not None:
                stack.append(node.get_right())
        """

class NTree:
    def __init__(self, labelled_tree, root):
        self.binary_tree = copy.deepcopy(labelled_tree)
        self.n_ary_tree = LabelledClusterNode(root)

    def create_n_nary_tree(self):
        queue = [self.binary_tree]
        while queue:
            node = queue.pop(0)
            if node.head is None and node.parent is not None:
                node.head = node
                self.n_ary_tree.children_list.append(node)

            temp_child_list = []
            if node.get_left() is not None:
                temp_child_list.append(node.get_left())
            if node.get_right() is not None:
                temp_child_list.append(node.get_right())
            for v in temp_child_list:
                if v.label is not node.label:
                    v.parent = node.head
                elif v.label is node.label:
                    v.parent = node.parent
                    v.head = node.head

        queue = [self.n_ary_tree]
        while queue:
            node = queue.pop(0)
            for v in node.children_list:
                queue.append(v)
            print node.label

def cluster(db):
    with open(str(db.database) + '_vectors.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        list_of_keyword_to_weights = [rows for rows in reader]

    tickets_to_weights_matrix = numpy.zeros((len(list_of_keyword_to_weights), len(list_of_keyword_to_weights[0])))

    for i in range(len(list_of_keyword_to_weights)):
        for j in range(len(list_of_keyword_to_weights[0])):
            word_key = list_of_keyword_to_weights[i].keys()[j]
            tickets_to_weights_matrix[i, j] = list_of_keyword_to_weights[i][word_key]

    print tickets_to_weights_matrix.shape

    Z = linkage(tickets_to_weights_matrix, 'average')

    c, coph_dists = cophenet(Z, pdist(tickets_to_weights_matrix))

    print "Cophenetic Correlation: {}".format(c)

    root_node = to_tree(Z, rd=False)
    BTL = LabelledBT(root_node, list_of_keyword_to_weights)
    BTL.create_label_tree()
    #HNT = NTree(BTL, root_node)
    #HNT.create_n_nary_tree()

"""
    def llf(id):
        return str(list_of_keyword_to_weights[0].keys()[id])

    pyplot.figure(figsize=(25, 10))
    pyplot.title('Hierarchical Clustering Dendrogram')
    pyplot.xlabel('Sample Index (Cluster Size)')
    pyplot.ylabel('Distance')
    dendrogram(Z,
               #leaf_rotation=90,
               leaf_font_size=14,
               truncate_mode='lastp',
               p=4,
               show_contracted=True)
               #leaf_label_func=llf)
    #pyplot.show()
"""
"""
def create_similariy_matrix(db, list_of_keyword_vectors):
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
"""