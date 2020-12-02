import unittest
from typing import *
import random

from src.data_structures.tree.binary_tree import BinaryTree, BinaryNode
from src.data_structures.utils.utils import default_comparator

if __name__ == "__main__":
    tree = BinaryTree()
    tree.insert(1)
    tree.insert(2)
    tree.insert(3)
    tree.insert(4)