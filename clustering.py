import nltk
import csv
import numpy
import math
from matplotlib import pyplot
from scipy.cluster.hierarchy import *#dendrogram, linkage, cophenet
from scipy.spatial.distance import pdist
from peewee import *
import copy
import pygraphviz as pg
from collections import OrderedDict


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
    def __init__(self, root, list_of_keyword_to_weights, system_name):
        self.binary_tree = LabelledClusterNode(root)
        self.list_of_keyword_to_weights = list_of_keyword_to_weights
        self.system_name = system_name

    def generate_keywords_label(self, nid):
        keyword_weights = self.list_of_keyword_to_weights[nid]

        # First cast dictionary values to int
        for keyword in keyword_weights.keys():
            keyword_weights[keyword] = int(keyword_weights[keyword])

        # Sort according to value
        keyword_weights = OrderedDict(sorted(keyword_weights.items(), key=lambda t: t[1], reverse=True))
        nonzero_keywords = []

        count = 0
        for keyword in keyword_weights:
            if count >= 2:
                break
            if keyword_weights[keyword] > 0:
                nonzero_keywords.append(keyword)
                count += 1

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


def draw_tree(BT):
    A = pg.AGraph(directed=True, strict=True)

    level = 0
    # BFS trough the tree and draw first 300 nodes
    queue = [BT.binary_tree]
    while queue:
        node = queue.pop(0)
        if node.parent is not None:
            if node.parent.label != node.label:
                A.add_edge(node.parent.label, node.label)

        level += 1
        if node.get_left() is not None:
            queue.append(node.get_left())
        if node.get_right() is not None:
            queue.append(node.get_right())
        if level >= 300:
            break
    A.write('{}.dot'.format(BT.system_name))
    A.layout(prog='dot')
    A.draw('{}.png'.format(BT.system_name))
    print "Generated tree drawing."


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
    BTL = LabelledBT(root_node, list_of_keyword_to_weights, str(db.database))
    BTL.create_label_tree()
    draw_tree(BTL)
