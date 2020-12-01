from dataclasses import dataclass
from typing import *


@dataclass
class Node:
    parent: "Node"
    children: List["Node"]


C = Node(None, None)
B = Node(None, None)
A = Node(None, None)

A.parent = B
B.parent = C
C.children = [B]
B.children = [A]

C.children[0].parent = None


print(B.children[0].parent.parent is B.parent)
