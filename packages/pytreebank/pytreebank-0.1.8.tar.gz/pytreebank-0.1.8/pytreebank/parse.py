import re
import codecs
from .labeled_trees       import LabeledTree
from .labeled_tree_corpus import LabeledTreeCorpus

find_bubbles = re.compile(r'(\([^\(\)]+\))')

class ParseError(Exception):
    def __init__(self, message):
        self.message = message

def create_leaves_from_string(line):
    matches = re.findall(find_bubbles, line)
    for match in matches:
        yield create_tree_from_string(match)

def attribute_sentence_label(node, current_word):
    node.sentence = current_word\
        .replace("\xa0", " ")\
        .replace("\\", "")\
        .replace("-LRB-", "(")\
        .replace("-RRB-", ")")\
        .replace("-LCB-", "{")\
        .replace("-RCB-", "}")\
        .replace("-LSB-", "[")\
        .replace("-RSB-", "]")
    node.sentence = node.sentence .strip(" ")
    node.udepth = 1
    if len(node.sentence) > 0 and node.sentence[0].isdigit():
        split_sent = node.sentence.split(" ", 1)
        label = split_sent[0]
        if len(split_sent) > 1:
            sentence = split_sent[1]
            node.sentence = sentence
        node.label = int(label)

    if len(node.sentence) == 0:
        node.sentence = None

def create_tree_from_string(line):
    depth         = 0
    current_word  = ""
    root          = None
    current_node  = root

    for char in line:

        if char == '(':
            if current_node is not None and len(current_word) > 0:
                attribute_sentence_label(current_node, current_word)
                current_word = ""
            depth += 1
            if depth > 1:
                # replace current head node by this node:
                child = LabeledTree(depth=depth)
                current_node.add_child(child)
                current_node = child
                root.add_general_child(child)
            else:
                root = LabeledTree(depth=depth)
                root.add_general_child(root)
                current_node = root

        elif char == ')':

            # assign current word:
            if len(current_word) > 0:
                attribute_sentence_label(current_node, current_word)
                current_word = ""

            # go up a level:
            depth -= 1
            if current_node.parent != None:
                current_node.parent.udepth = max(current_node.udepth+1, current_node.parent.udepth)
            current_node = current_node.parent
        else:
            # add to current read word
            current_word += char
    if depth != 0:
        raise ParseError("Not an equal amount of closing and opening parentheses")

    return root

def check_udepth(tree):
    depths = depth_sorted_children(tree)
    for i in reversed(range(1, depths[-1]+1)):
        for tree in depths[i]:
            if len(tree.children) == 0:
                assert(tree.udepth == 1)
            else:
                assert(tree.udepth == max([i.udepth for i in tree.children]) + 1)
    return tree

def import_tree_corpus_words(trees):
    tree_list = LabeledTreeCorpus()
    with codecs.open(trees, "r", "UTF-8") as f:
        for line in f:
            for tree in create_leaves_from_string(line):
                tree_list.append(tree)
    return tree_list

def import_tree_corpus(trees):
    tree_list = LabeledTreeCorpus()
    with codecs.open(trees, "r", "UTF-8") as f:
        for line in f:
            tree_list.append(create_tree_from_string(line))
    return tree_list

