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
from collections import OrderedDict, Counter
import util

class LabelledClusterNode(ClusterNode):
    """
    Custom ClusterNode class for use in binary or n-ary trees.
    """
    def __init__(self, cn):
        ClusterNode.__init__(self, cn.get_id(), cn.get_left(), cn.get_right(), 0)
        self.label = None
        self.parent = None
        self.children_list = []
        self.num_leaf_nodes = 1
        self.head = None


class LabelledTree:
    def __init__(self, root, list_of_keyword_to_weights, system_name):
        self.tree = LabelledClusterNode(root)
        self.list_of_keyword_to_weights = list_of_keyword_to_weights
        self.system_name = system_name

    def generate_keywords_label(self, nid):
        keyword_weights = self.list_of_keyword_to_weights[nid]

        # TODO: Need to cache this for speedup
        # First cast dictionary values to int
        for keyword in keyword_weights.keys():
            keyword_weights[keyword] = int(keyword_weights[keyword])

        # Sort according to value
        keyword_weights = OrderedDict(sorted(keyword_weights.items(), key=lambda t: t[1], reverse=True))
        nonzero_keywords = []

        for keyword in keyword_weights:
            if keyword_weights[keyword] > 0:
                nonzero_keywords.append(keyword)

        return nonzero_keywords

    def create_label_tree(self):
        # DFS through scipy tree and convert to label leaf nodes according to T
        stack = [self.tree]
        parents = []
        while stack:
            node = stack.pop()
            nid = node.get_id()

            # This checks if left is None, which would make it a leaf
            if node.is_leaf():
                node.label = self.generate_keywords_label(nid)
            else:
                node.left = LabelledClusterNode(node.get_left())
                left_child = node.get_left()

                stack.append(left_child)
                left_child.parent = node
                parents.append(node)

            if node.get_right() is not None:
                node.right = LabelledClusterNode(node.get_right())
                right_child = node.get_right()

                stack.append(right_child)
                right_child.parent = node

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

    def generate_bt_stats(self, node):
        if node is None:
            return 0
        if node.is_leaf():
            return 1
        return self.generate_bt_stats(node.get_left()) + self.generate_bt_stats(node.get_right())

    def generate_leaf_statistics(self, node, cache):
        if cache[node.get_id()] != 0:
            return cache[node.get_id()]

        if len(node.children_list) == 0:
            cache[node.get_id()] = 1
            return 1

        result = 0
        for child in node.children_list:
            result += self.generate_leaf_statistics(child, cache)
        cache[node.get_id()] = result
        return result

    def create_nary_from_label_tree(self):
        queue = [self.tree]

        while queue:
            node = queue.pop(0)
            left_child = node.get_left()
            right_child = node.get_right()
            self.merge_or_add_child(left_child, node, queue)
            self.merge_or_add_child(right_child, node, queue)

        # Generate statistics of each node by recursive DFS
        cache = Counter()
        stack = [self.tree]
        while stack:
            node = stack.pop()
            node.num_leaf_nodes = self.generate_leaf_statistics(node, cache)
            for child in node.children_list:
                stack.append(child)

        print self.tree.num_leaf_nodes

    @staticmethod
    def merge_or_add_child(child, node, queue):
        if child is None:
            return
        queue.append(child)

        # A unique node was found, so it is set as head of sequence. This starts off the propagation.
        if node.head is None:
            node.head = node

        # A duplicate child was found, so its head will be set to this node's head (set previously).
        # This step propagates the head's reference down the tree until it hits a unique node.
        # When a unique node is found, it will add that unique node to the head's list, and the process starts over.
        if str(child.label) == str(node.label):
            child.head = node.head
        else:
            node.head.children_list.append(child)


def draw_binary_tree(Tree):
    A = pg.AGraph(directed=True, strict=True)

    level = 0
    queue = [Tree.tree]
    while queue:
        node = queue.pop(0)
        node_string = str(node.label[:2]) + '\n' + str(Tree.generate_bt_stats(node))

        if node.parent is not None:
            parent_string = str(node.parent.label[:2]) + '\n' + str(Tree.generate_bt_stats(node.parent))
            A.add_edge(parent_string, node_string)

        level += 1
        if node.get_left() is not None:
            queue.append(node.get_left())
        if node.get_right() is not None:
            queue.append(node.get_right())
        if level >= 50:
            break

    util.ensure_path_exists(util.cwd + '/dot/')
    dot_path = util.cwd + '/dot/'
    A.write('{}{} BT.dot'.format(dot_path, Tree.system_name))
    A.layout(prog='dot')
    A.draw('{}{} BT.png'.format(dot_path, Tree.system_name))


def draw_nary_tree(Tree):
    A = pg.AGraph(directed=True, strict=True)

    # BFS trough the tree and draw first 300 nodes
    level = 0
    queue = [Tree.tree]
    while queue:
        node = queue.pop(0)
        node_string = str(node.label[:2]) + '\n' + str(node.num_leaf_nodes)

        for child in node.children_list:
            child_string = str(child.label[:2]) + '\n' + str(child.num_leaf_nodes)
            A.add_edge((node_string, child_string))

            queue.append(child)
            level += 1
        if level >= 100:
            break

    util.ensure_path_exists(util.cwd + '/dot/')
    dot_path = util.cwd + '/dot/'
    A.write('{}{} NT.dot'.format(dot_path, Tree.system_name))
    A.layout(prog='dot')
    A.draw('{}{} NT.png'.format(dot_path, Tree.system_name))


def cluster(db):
    vector_path = util.cwd + '/vectors/'
    with open(vector_path + str(db.database) + '_vectors.csv', 'r') as csvfile:
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
    Tree = LabelledTree(root_node, list_of_keyword_to_weights, str(db.database))
    Tree.create_label_tree()
    #draw_binary_tree(Tree)
    Tree.create_nary_from_label_tree()
    draw_nary_tree(Tree)
    print "Generated tree drawings."
