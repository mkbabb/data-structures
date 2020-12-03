import math
from typing import *

from typing_extensions import *

from src.data_structures.utils.utils import is_power_of
from src.data_structures.list.list import Vector

T = TypeVar("T")

class Node(Generic[T]):
    def __init__(self, tree_order: int,  children: Optional[List[T]] = None, )




class Trie(Generic[T]):
    def __ini__(self)