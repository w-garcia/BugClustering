import csv
import numpy
from config import config as cfg
from scipy.cluster.hierarchy import *
from scipy.spatial.distance import pdist
from scipy import clip
from peewee import *
import pygraphviz as pg
from collections import OrderedDict, Counter
import util
import DBModel
import math


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
    """
    Data structure representing a tree and its meta data.
    self.tree is first created by replicating the scipy binary tree generated by Linkage.
    Each node is then transformed into a LabelledClusterNode, which inherits the original scipy node class.
    Next, labels are generated for each leaf node based on node id (which corresponds to the index of the data)
    After all leaves are labelled, the parents are labelled according to the intersection of its children's labels.
    This labelled binary tree is then transformed into an n-ary tree, which can be drawn with pygraphviz.
    """
    def __init__(self, root, list_of_keyword_to_weights, system_name):
        self.tree = LabelledClusterNode(root)
        self.list_of_keyword_to_weights = list_of_keyword_to_weights
        self.system_name = system_name

    def generate_keywords_label(self, nid):
        keyword_weights = self.list_of_keyword_to_weights[nid]

        # TODO: Need to cache this for speedup
        # First cast dictionary values to float
        for keyword in keyword_weights.keys():
            keyword_weights[keyword] = float(keyword_weights[keyword])

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

        #print self.tree.num_leaf_nodes

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


def draw_binary_tree(Tree, filepath, max_tree_size):
    A = pg.AGraph(directed=True, strict=True)

    level = 0
    queue = [Tree.tree]
    while queue:
        node = queue.pop(0)
        node_string = str(node.label) + '\n' + str(Tree.generate_bt_stats(node))

        if node.parent is not None:
            parent_string = str(node.parent.label) + '\n' + str(Tree.generate_bt_stats(node.parent))
            A.add_edge(parent_string, node_string)

        level += 1
        if node.get_left() is not None:
            queue.append(node.get_left())
        if node.get_right() is not None:
            queue.append(node.get_right())
        if level >= max_tree_size:
            break

    dot_path = util.cwd + '/dot' + filepath
    util.ensure_path_exists(dot_path)
    A.write('{}{} BT.dot'.format(dot_path, Tree.system_name))
    A.layout(prog='dot')
    A.draw('{}{} BT.png'.format(dot_path, Tree.system_name))
    print "[Clustering] : Created binary tree at path {}.".format('{}{} BT.png'.format(dot_path, Tree.system_name))


def create_node_string(node):
    node_string = node.label
    return str(node_string) + '\n' + str(node.num_leaf_nodes)


def draw_nary_tree(Tree, max_tree_size, correlation, c='none'):
    A = pg.AGraph(directed=True, strict=True)

    # Get value thats 1% of total nodes in tree
    num_leaf_nodes_cutoff = int(0.01 * Tree.tree.num_leaf_nodes)
    print "[Clustering] : Leaf node cutoff: {}.".format(num_leaf_nodes_cutoff)

    # BFS trough the tree and draw first 300 nodes
    level = 0
    queue = [Tree.tree]
    while queue:
        node = queue.pop(0)
        level += 1

        node_string = create_node_string(node)

        for child in node.children_list:
            # Skip this node if it doesn't meet the 1% cutoff requirement
            if child.num_leaf_nodes < num_leaf_nodes_cutoff:
                continue

            # Create child string so only words not in parent are displayed.
            child_string = create_node_string(child)
            A.add_edge((node_string, child_string))
            queue.append(child)

        if level >= max_tree_size:
            break

    dot_path = util.generate_meta_path(Tree.system_name, 'dot', c)
    util.ensure_path_exists(dot_path)
    A.write('{}{} NT.dot'.format(dot_path, Tree.system_name))
    A.layout(prog='dot')
    A.draw('{}{} NT Score={}.png'.format(dot_path, Tree.system_name, correlation))
    print "[Clustering] : Created n-ary tree at path {}.".format('{}{} NT Score={}.png'.format(dot_path,
                                                                                               Tree.system_name,
                                                                                               correlation))


def cluster(system_name):
    class_clustering_filter = cfg.class_clustering_filter
    systems_filter = cfg.systems_filter
    max_tree_size = cfg.max_tree_size

    if class_clustering_filter == 'none':
        cluster_by_all(system_name, max_tree_size)
    else:
        cluster_by_filter(system_name, systems_filter, class_clustering_filter, max_tree_size)
    print "[Status] : Generated tree drawings."


def cluster_by_all(system_name, max_tree_size):
    vector_path = util.generate_meta_path(system_name, 'vectors')
    filename = vector_path + system_name + '_vectors.csv'

    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        list_of_keyword_to_weights = [rows for rows in reader]

    if len(list_of_keyword_to_weights) < 1:
        print "[Warning] : Not enough tickets to generate clusters. Skipping..."
        return

    tickets_to_weights_matrix = construct_matrix(list_of_keyword_to_weights)

    if tickets_to_weights_matrix.shape[0] < 2:
        print "[Warning] : Not enough tickets to generate clusters. Skipping..."
        return

    method = cfg.cluster_similarity_method
    metric = cfg.distance_metric

    Y = pdist(tickets_to_weights_matrix, metric=metric)
    Y = Y[~numpy.isnan(Y)]

    Z = linkage(Y, method=method, metric=metric)

    correlation, coph_dists = cophenet(Z, Y)

    print "[Status] : Cophenetic Correlation: {}".format(correlation)

    root_node = to_tree(Z, rd=False)
    Tree = LabelledTree(root_node, list_of_keyword_to_weights, system_name)
    Tree.create_label_tree()

    #draw_binary_tree(Tree, tree_path, max_tree_size)
    Tree.create_nary_from_label_tree()
    draw_nary_tree(Tree, max_tree_size, correlation)


def construct_matrix(list_of_keyword_to_weights):
    tickets_to_weights_matrix = numpy.zeros((len(list_of_keyword_to_weights), len(list_of_keyword_to_weights[0])))
    # Construct matrix of weights as integer only numpy matrix
    for i in range(len(list_of_keyword_to_weights)):
        for j in range(len(list_of_keyword_to_weights[0])):
            word_key = list_of_keyword_to_weights[i].keys()[j]
            tickets_to_weights_matrix[i, j] = list_of_keyword_to_weights[i][word_key]

    print "[Status] : Shape is {}".format(tickets_to_weights_matrix.shape)

    return tickets_to_weights_matrix


def cluster_by_filter(system_name, topology_filter, clustering_filter, max_tree_size):
    classes_to_keep = set()

    if topology_filter == 'none':
        selection = DBModel.LFF_Keywords.select()
    else:
        selection = DBModel.LFF_Keywords.select_by_system(system_name)

    for row in selection:
        classes = row.classification.split(' ')

        for c in classes:
            c = c.encode()
            if len(c) < 2 or c in classes_to_keep:
                continue
            elif clustering_filter is None:
                classes_to_keep.add(c)
            elif c.startswith(clustering_filter):
                classes_to_keep.add(c)

    for c in classes_to_keep:
        vector_path = util.generate_meta_path(system_name, 'vectors', c)
        filename = vector_path + system_name + '_vectors.csv'

        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            list_of_keyword_to_weights = [rows for rows in reader]

        if len(list_of_keyword_to_weights) < 1:
            print "[Warning] : Not enough tickets to generate clusters. Skipping..."
            continue

        tickets_to_weights_matrix = construct_matrix(list_of_keyword_to_weights)

        if tickets_to_weights_matrix.shape[0] < 2:
            print "[Warning] : Not enough tickets to generate clusters. Skipping..."
            continue

        method = cfg.cluster_similarity_method
        metric = cfg.distance_metric

        Y = pdist(tickets_to_weights_matrix, metric=metric)
        Y = Y[~numpy.isnan(Y)]

        Z = linkage(Y, method=method, metric=metric)

        correlation, coph_dists = cophenet(Z, Y)

        print "[Status] : Cophenetic Correlation: {}".format(correlation)

        root_node = to_tree(Z, rd=False)
        Tree = LabelledTree(root_node, list_of_keyword_to_weights, system_name)
        Tree.create_label_tree()

        # draw_binary_tree(Tree, tree_path, max_tree_size)
        Tree.create_nary_from_label_tree()
        draw_nary_tree(Tree, max_tree_size, correlation, c)

        print "[Status] : Tree generated for {}.".format(c)
