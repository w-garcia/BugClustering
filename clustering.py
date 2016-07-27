import csv
import numpy
from config import config as cfg
from scipy.cluster.hierarchy import *
from scipy.spatial.distance import pdist
import pygraphviz as pg
from collections import OrderedDict, Counter, defaultdict
import util
import DBModel
from Ticket import Ticket


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
        self.ground_truth = []
        self.ticket = None
        self.path_of_interest = False


class LabelledTree:
    """
    Data structure representing a tree and its meta data.
    self.tree is first created by replicating the scipy binary tree generated by Linkage.
    Each node is then transformed into a LabelledClusterNode, which inherits the original scipy node class.
    Next, labels are generated for each leaf node based on node id (which corresponds to the index of the data)
    After all leaves are labelled, the parents are labelled according to the intersection of its children's labels.
    This labelled binary tree is then transformed into an n-ary tree, which can be drawn with pygraphviz.
    """
    def __init__(self, root, system_name, list_of_tickets):
        self.tree = LabelledClusterNode(root)
        self.list_of_tickets = list_of_tickets
        self.system_name = system_name

    @staticmethod
    def build_keyword_to_weight_dict_from_ticket(ticket_of_interest):
        list_nonzero_weights = ticket_of_interest.nonzero_vector
        list_keywords = ticket_of_interest.keywords

        kw_to_weight_dict = {}
        for i in range(len(list_nonzero_weights)):
            kw_to_weight_dict[list_keywords[i]] = list_nonzero_weights[i]

        return kw_to_weight_dict

    def generate_keywords_label(self, nid):
        keyword_weights = self.build_keyword_to_weight_dict_from_ticket(ticket_of_interest=self.list_of_tickets[nid])

        # Sort according to value
        return OrderedDict(sorted(keyword_weights.items(), key=lambda t: t[1], reverse=True)).keys()

    def generate_ground_truth(self, nid):
        ticket_of_interest = self.list_of_tickets[nid]
        raw_list = ticket_of_interest.classes.split(' ')
        truth_list = set()

        # Only keep class categories from our classes of interest
        for c in raw_list:
            for ci in cfg.classes_of_interest:
                if ci in c:
                    truth_list.add(c)
                    truth_list.add(ci)

        # Sort such that labels are identical
        return sorted(list(truth_list))

    @staticmethod
    def mark_node_of_interest(node):
        if len(node.ticket.classes) == 0:
            return True
        else:
            return False

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
                node.ground_truth = self.generate_ground_truth(nid)
                node.ticket = self.list_of_tickets[nid]
                node.path_of_interest = self.mark_node_of_interest(node)
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
                parents[i].ground_truth = left_child.ground_truth
            else:
                intersection = set.intersection(set(left_child.label), set(right_child.label))
                if not intersection:
                    parents[i].label = ['unknown']
                else:
                    parents[i].label = list(intersection)

                class_intersection = set.intersection(set(left_child.ground_truth), set(right_child.ground_truth))
                if not class_intersection:
                    # Check if child tickets are unlabelled. The goal is to pick size of training data such that it
                    # is much larger than the size of testing/labelling data, otherwise both children can end up
                    # unlabelled, which is a dead-end (making the clustering useless)

                    if left_child.ground_truth == []:
                        # Use the other child's ground truth since that is the only info we have.
                        parents[i].ground_truth = right_child.ground_truth
                    elif right_child.ground_truth == []:
                        # Same as above.
                        parents[i].ground_truth = left_child.ground_truth
                    else:
                        # Either both children are empty, or the clustered tickets are simply not related to each other.
                        parents[i].ground_truth = ['unknown']
                else:
                    parents[i].ground_truth = list(class_intersection)
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

        # Generate statistics of each node by recursive DFS, and mark paths of interest. Also assign parents.
        cache = Counter()
        interest_cache = Counter()
        stack = [self.tree]
        while stack:
            node = stack.pop()
            node.num_leaf_nodes = self.generate_leaf_statistics(node, cache)
            if cfg.clustering_mode != 'vanilla':
                node.path_of_interest = self.mark_paths_of_interest(node, interest_cache)
            for child in node.children_list:
                child.parent = node
                stack.append(child)

    @staticmethod
    def merge_or_add_child(child, node, queue):
        if child is None:
            return
        queue.append(child)

        # A unique node was found, so it is set as head of sequence. This starts off the propagation.
        if node.head is None:
            node.head = node

        # Decide which values to use for comparison based off config
        if cfg.node_label_display == 'class':
            child_comparison_string = str(child.ground_truth)
            node_comparison_string = str(node.ground_truth)
        else:
            child_comparison_string = str(child.label)
            node_comparison_string = str(node.label)

        # A duplicate child was found, so its head will be set to this node's head (set previously).
        # This step propagates the head's reference down the tree until it hits a unique node.
        # When a unique node is found, it will add that unique node to the head's list, and the process starts over.
        if child_comparison_string == node_comparison_string:
            child.head = node.head
        else:
            node.head.children_list.append(child)

    def mark_paths_of_interest(self, node, interest_cache):
        if interest_cache[node.get_id()] == 1:
            return True

        if node.path_of_interest:
            interest_cache[node.get_id()] = 1
            print "[clustering] : <-> Found node of interest"
            return True

        for child in node.children_list:
            if self.mark_paths_of_interest(child, interest_cache):
                print "[clustering] :  | "
                return True
        return False


def draw_binary_tree(Tree, correlation, c='none'):
    A = pg.AGraph(directed=True, strict=True)

    level = 0
    queue = [Tree.tree]
    while queue:
        node = queue.pop(0)
        #node_string = str(node.label) + '\n' + str(Tree.generate_bt_stats(node))
        node_string = str(node.ground_truth) + '\n' + str(Tree.generate_bt_stats(node))

        level += 1
        if node.get_left() is not None:
            queue.append(node.get_left())
            child_string = str(node.get_left().ground_truth) + '\n' + str(Tree.generate_bt_stats(node.get_left()))
            A.add_edge(node_string, child_string)
        if node.get_right() is not None:
            queue.append(node.get_right())
            child_string = str(node.get_right().ground_truth) + '\n' + str(Tree.generate_bt_stats(node.get_right()))
            A.add_edge(node_string, child_string)
        if level >= cfg.max_tree_size:
            break

    dot_path = util.generate_meta_path(Tree.system_name, 'dot', c)
    util.ensure_path_exists(dot_path)
    A.write('{}{} BT.dot'.format(dot_path, Tree.system_name))
    A.layout(prog='dot')
    A.draw('{}{} BT Score={}.png'.format(dot_path, Tree.system_name, correlation))
    print "[clustering] : Created n-ary tree at path {}.".format('{}{} BT Score={}.png'.format(dot_path,
                                                                                               Tree.system_name,
                                                                                               correlation))


def create_node_string(node):
    if cfg.node_label_display == 'class':
        node_string = str(node.ground_truth)
    elif cfg.node_label_display == 'both':
        node_string = str(node.label) + '\n' + str(node.ground_truth)
    else:
        node_string = str(node.label)

    if node.ticket is not None:
        node_string = node_string + '\nid: ' + str(node.ticket.id)

    if cfg.draw_leaf_statistics:
        node_string = node_string + '\n' + str(node.num_leaf_nodes)

    return node_string


def draw_nary_tree(Tree, correlation, c='none'):
    A = pg.AGraph(directed=True, strict=True)

    # Get value thats 1% of total nodes in tree
    num_leaf_nodes_cutoff = int(0.01 * cfg.node_cutoff_percentage * Tree.tree.num_leaf_nodes)
    print "[clustering] : Leaf node cutoff: {}.".format(num_leaf_nodes_cutoff)

    # BFS trough the tree and draw first 300 nodes
    count = 0
    queue = [Tree.tree]
    while queue:
        node = queue.pop(0)

        if count >= cfg.max_tree_size:
            break

        node_string = create_node_string(node)

        for child in node.children_list:
            # Force draw if node is on path of interest
            if cfg.clustering_mode != 'vanilla' and child.path_of_interest:
                child_string = create_node_string(child)
                A.add_edge((node_string, child_string), color='blue')
                queue.append(child)
                if len(child.children_list) == 0:
                    child_node = A.get_node(child_string)
                    child_node.attr['color'] = 'blue'
                continue

            # Skip this node if it doesn't meet the 1% cutoff requirement
            if child.num_leaf_nodes < num_leaf_nodes_cutoff:
                continue

            child_string = create_node_string(child)
            # If the config allows, skip the node if it will result in repeated node (and thus a cycle for pygraphviz)
            # This will fail if draw_leaf_statistics is active, since leaf stats make the labels unique
            if cfg.skip_repeated_nodes and child_string == node_string:
                continue

            count += 1
            A.add_edge((node_string, child_string))
            queue.append(child)

    dot_path = util.generate_meta_path(Tree.system_name, 'dot', c)
    util.ensure_path_exists(dot_path)
    A.write('{}{} NT.dot'.format(dot_path, Tree.system_name))
    A.layout(prog='dot')
    A.draw('{}{} NT Score={}.png'.format(dot_path, Tree.system_name, correlation))
    print "[clustering] : Created n-ary tree at path {}.".format('{}{} NT Score={}.png'.format(dot_path,
                                                                                               Tree.system_name,
                                                                                               correlation))


def get_prediction(Tree):
    # DFS through tree and find the parent of leaf interest path.
    stack = [Tree.tree]
    while stack:
        node = stack.pop()

        if node.path_of_interest and len(node.children_list) == 0:
            return node.parent.ground_truth

        for child in node.children_list:
            stack.append(child)

    return []


def cluster(system_name, prediction=None):
    class_clustering_filter = cfg.class_clustering_filter
    systems_filter = cfg.systems_filter

    if class_clustering_filter == 'none':
        cluster_by_all(system_name, prediction)
    else:
        cluster_by_filter(system_name, systems_filter, class_clustering_filter, prediction)
    print "[status] : Generated clusters."


def cluster_by_all(system_name, prediction=None):
    vector_path = util.generate_meta_path(system_name, 'vectors')
    filename = vector_path + system_name + '_vectors.csv'

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

    method = cfg.cluster_similarity_method
    metric = cfg.distance_metric

    Y = pdist(tickets_to_weights_matrix, metric=metric)
    Y = Y[~numpy.isnan(Y)]

    Z = linkage(Y, method=method, metric=metric)

    correlation, coph_dists = cophenet(Z, Y)

    print "[{}] : Cophenetic Correlation: {}".format(system_name, correlation)

    root_node = to_tree(Z, rd=False)
    list_of_tickets = build_ticket_list(list_of_ticket_dicts)
    Tree = LabelledTree(root_node, system_name, list_of_tickets)
    Tree.create_label_tree()
    #draw_binary_tree(Tree, correlation)
    Tree.create_nary_from_label_tree()
    if cfg.clustering_mode != 'vanilla':
        prediction.append(get_prediction(Tree))

    if cfg.draw_trees:
        draw_nary_tree(Tree, correlation)
        print "[{}] : Tree generated.".format(system_name, system_name)


def build_ticket_list(list_of_ticket_dicts):
    ticket_list = []
    for ticket_dict in list_of_ticket_dicts:
        desc = ticket_dict['description']
        id = ticket_dict['id']
        classes = ticket_dict['classification']
        system = ticket_dict['system']
        vector = [float(x) for x in ticket_dict['vector'].split(' ')]
        keywords = [word for word in ticket_dict['keywords'].split(' ')]
        t = Ticket(id, desc, classes, system, vector, keywords)
        ticket_list.append(t)

    return ticket_list


def construct_matrix(list_of_weights):
    # Build a numpy matrix of m x n, where m is number of documents and n is number of keywords
    tickets_to_weights_matrix = numpy.zeros((len(list_of_weights), len(list_of_weights[0].split(' '))))

    m = len(list_of_weights)
    # Construct matrix of weights as integer only numpy matrix
    for i in range(m):
        list_of_float_weights = [float(x) for x in list_of_weights[i].split(' ')]
        n = len(list_of_float_weights)

        for j in range(n):
            tickets_to_weights_matrix[i, j] = list_of_float_weights[j]

    print "[status] : Shape is {}".format(tickets_to_weights_matrix.shape)

    return tickets_to_weights_matrix


def cluster_by_filter(system_name, topology_filter, clustering_filter, prediction=None):
    classes_to_keep = set()

    if topology_filter == 'none':
        selection = DBModel.LFF_Keywords.select()
    else:
        selection = DBModel.LFF_Keywords.get_db_ref_by_system(system_name).select()

    # Create list of classes of to be clustered according to filter
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

    # Add the filter of interest to build a non-truth cluster
    classes_to_keep.add(clustering_filter)

    for c in classes_to_keep:
        # Load file assuming it was created previously for this class
        vector_path = util.generate_meta_path(system_name, 'vectors', c)
        filename = vector_path + system_name + '_vectors.csv'

        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            list_of_ticket_dicts = [rows for rows in reader]

        if len(list_of_ticket_dicts) < 1:
            print "[warning] : Not enough tickets to generate clusters. Skipping..."
            continue

        # Create list of keyword weights, keeping string format
        list_of_weights = [ticket_dict['vector'] for ticket_dict in list_of_ticket_dicts]

        # Construct matrix from the list of keyword dictionaries
        tickets_to_weights_matrix = construct_matrix(list_of_weights)

        if tickets_to_weights_matrix.shape[0] < 2:
            print "[warning] : Not enough tickets to generate clusters. Skipping..."
            continue

        method = cfg.cluster_similarity_method
        metric = cfg.distance_metric

        Y = pdist(tickets_to_weights_matrix, metric=metric)
        Y = Y[~numpy.isnan(Y)]

        Z = linkage(Y, method=method, metric=metric)

        correlation, coph_dists = cophenet(Z, Y)

        print "[{}:{}] : Cophenetic Correlation: {}".format(system_name, c, correlation)

        list_of_tickets = build_ticket_list(list_of_ticket_dicts)
        root_node = to_tree(Z, rd=False)
        Tree = LabelledTree(root_node, system_name, list_of_tickets)
        Tree.create_label_tree()

        # draw_binary_tree(Tree, tree_path)
        Tree.create_nary_from_label_tree()
        if cfg.draw_trees:
            draw_nary_tree(Tree, correlation, c)

        print "[{}:{}] : Tree generated.".format(system_name, c)
