import math
from typing import *

from typing_extensions import *

from ..utils.utils import is_power_of

__all__ = ["Vector", "Node", "WIDTH", "get_tree_depth"]

T = TypeVar("T")
S = TypeVar("S")

# Constants that define the shape of the tree structure.
# In production, BITS would likely be log_2(32) = 5, like that of Clojure's
# Vector implemenetation.

# Levels of the tree, also used to slice up a given index into
# the vector into BITS intervals. So 4 = b0100 would be broken up into
# 01 and 00.
BITS = 2
# Width of the leaf nodes.
WIDTH = 1 << BITS
# Mask to slice up the aforesaid index, or key.
MASK = WIDTH - 1


NodeType = List[Union[Optional[T], "Node[T]"]]


class Node(Generic[T]):
    def __init__(self, children: Optional[NodeType[T]] = None):
        if children is not None:
            self.children = children + [None] * (WIDTH - len(children))
        else:
            self.children = [None] * WIDTH

    def copy(self):
        return Node(list(self.children))


def get_tree_depth(length: int) -> int:
    return 0 if length == 0 else math.floor(math.log(length, WIDTH))


class Vector(Sequence[T]):
    def __init__(self, vals: List[T]):
        self.root: Node[T] = Node()
        self.length = 0
        self.mutation = False

        self.mutate()
        for val in vals:
            self.append(val)
        self.mutate()

    def __len__(self) -> int:
        return self.length

    @overload
    def __getitem__(self, key: int) -> T:
        pass

    @overload
    def __getitem__(self, key: slice) -> "Vector[T]":
        pass

    def __getitem__(self, key: Union[int, slice]) -> Union[T, "Vector[T]"]:
        if isinstance(key, slice):
            start, stop, step = key.indices(len(self))
            return Vector([self[i] for i in range(start, stop, step)])
        elif isinstance(key, int):
            key = key + self.length if key < 0 else key
            if key > self.length:
                raise IndexError
            else:
                return self._at(key)
        else:
            raise TypeError(f"Invalid argument type: {type(key)}")

    @staticmethod
    def _create(root: Node[T], length: int) -> "Vector":
        out: "Vector" = Vector([])
        out.root = root
        out.length = length
        return out

    @staticmethod
    def _reduce_node(
        key: int, reducer: Callable[[S, int, int], S], init: S, depth: int,
    ) -> S:
        """Low-level list reduction API.

        Args:
            key (int): leaf child key index. For example, if you wanted to grab the last element
            of an array of n elements, key = n.
            reducer (Callable[[S, int, int], S]): Reduction function that requires:
                a reducer value of type S,
                the current level in the tree **(0-indexed from the bottom up)**,
                a current index into said level. 
            init (S): initial value to reduce upon.
            depth (Optional[int], optional): depth to traverse down to. Defaults to the list's max depth.

        Returns:
            S: the reduced value.
        """
        acc = init

        for level in range(depth, 0, -1):
            ix = (key >> (level * BITS)) & MASK
            acc = reducer(acc, level, ix)

        return acc

    def _at(self, key: int, func: Optional[Callable[[int, Node[T]], S]] = None) -> S:
        """Returns an element located at index `key`.
        Takes an optional callback func that must return a leaf node value.
        """
        leaf_ix = key & MASK
        func = (
            func
            if func is not None
            else lambda leaf_ix, leaf: cast(S, leaf.children[leaf_ix])
        )

        def reducer(node: Node[T], level: int, ix: int) -> Node[T]:
            return node.children[ix]

        leaf = self._reduce_node(key, reducer, self.root, get_tree_depth(self.length))

        return func(leaf_ix, leaf)

    def mutate(self) -> None:
        self.mutation = not self.mutation

    def append(self, val: T) -> "Vector":
        """There's 3 cases when appending, in order initial possibility:
         1. Root overflow: there's no more space in the entire tree: thus we must
         create an entirely new root, whereof's left branch is the current root.

         2. There's no room in the left branch, and the right branch is None: thus we must
         create a right branch and fill its first element with "value".

         3. There's space in the current branch: we simply insert "value" here,
         path copying on the way down.
        """
        root = self.root
        length = self.length + 1
        key = self.length
        leaf_ix = key & MASK

        # Case 1.
        if is_power_of(length, WIDTH):
            root = Node([root])

        root = root.copy() if not self.mutation else root

        def reducer(node: Node[T], level: int, ix: int) -> Node[T]:
            # Case 2.
            children = node.children[ix]

            if children is None:
                node.children[ix] = Node()
            else:
                node.children[ix] = children.copy() if not self.mutation else children
            return node.children[ix]

        leaf = self._reduce_node(key, reducer, root, get_tree_depth(length))
        # Case 3.
        leaf.children[leaf_ix] = val

        if not self.mutation:
            return self._create(root, length)
        else:
            self.root = root
            self.length = length
            return self

    def pop(self) -> "Vector[T]":
        """There's 3 cases when popping, in order of initial possibility:
        1. Root underflow: the current length is a power of WIDTH, meaning our last call to 
        `append` created a dead branch: we trim this off at the root and continue to case 3.

        2. The right-most leaf node is all "None"s after popping: we set this entire node to None.

        3. The right-most leaf node has at least one element in it: we simply set it to None.
        """
        root = self.root
        length = self.length - 1
        key = self.length - 1
        leaf_ix = key & MASK

        # Case 1.
        if is_power_of(self.length, WIDTH):
            root = root.children[0]

        root = root.copy() if not self.mutation else root

        def reducer(nodes: Tuple[Node[T], Node[T]], level: int, ix: int):
            prev_node, node = nodes
            children = node.children[ix]

            node.children[ix] = children.copy() if not self.mutation else children

            # Case 2.
            if level == 1 and leaf_ix == 0:
                node.children[ix] = None
                return node, None
            else:
                return node, node.children[ix]

        prev_leaf, leaf = self._reduce_node(
            key, reducer, (root, root), get_tree_depth(length)
        )

        # Case 3.
        if leaf is not None:
            leaf.children[leaf_ix] = None

        if not self.mutation:
            return self._create(root, length)
        else:
            self.root = root
            self.length = length
            return self

    @staticmethod
    def of(*args: Any) -> "Vector":
        return Vector(list(args))

    def copy(self) -> "Vector[T]":
        out = self.append(None)
        return out.pop()

    def concat(self, *args: "Vector[T]") -> "Vector[T]":
        lists: List["Vector"] = list(args)
        base = self.copy() if not self.mutation else self

        # If our vector is currently mutating, we want to preserve that.
        # So we force a mutation regardless, and the restore our base vector
        # to its original state.
        mutation = self.mutation
        base.mutation = True
        for sub_list in lists:
            sub_list.for_each(lambda curr_val, i: base.append(curr_val))
        base.mutation = mutation

        return base

    def splice(self, start: int, vals: List[T]) -> "Vector":
        """Split the vector into two halves, the first in the range of [0, start), 
        the second in [start, end). Appends the input `vals` list to the end of
        the first half, then joins the two halves back together into a new Vector.
        """

        out_list: List[T] = []

        self.reduce(lambda acc, curr_val, i: acc.append(curr_val), out_list, 0, start)
        out_list += vals
        self.reduce(lambda acc, curr_val, i: acc.append(curr_val), out_list, start)

        return Vector(out_list)

    def slice(self, start: Optional[int] = None, end: Optional[int] = None) -> "Vector":
        """Slice the vector into a section starting at `start` and ending at `end`.
        If start is None, return a copy.
        If end is None, end = self.length + 1.
        If end is < 0, end's value wraps around; end += self.length.
        """
        if start is None:
            return self.copy()
        else:
            out = self.copy()
            return out[start:end]

    def _for_each_leaf(
        self,
        leaf_func: Callable[[Node[T], int, int], Any],
        start: int = 0,
        end: Optional[int] = None,
    ) -> None:
        """Optimized iteration over the vector: we save the leaf node value to reuse as long
        as we can, or until the current index & MASK == 0. Asymptotically equivalent to the
        naïve self.at loop, but more efficient in practice. 

        Args:
            leaf_func (Callable[[Node[T], int, int], Any]): callback that accepts:
             the current leaf,
             the current leaf index,
             the current overall index.
            start (int): starting position, defaults to 0.
            end (Optional[int]): ending position, defaults to self.length. If end < 0, end += self.length.
        """
        end = self.length if end is None else end + self.length if end < 0 else end
        saved_leaf = None

        def at_func(leaf_ix: int, leaf: Node[T]) -> Node[T]:
            return leaf

        for i in range(start, end):
            leaf_ix = i & MASK

            if leaf_ix == 0 or saved_leaf is None:
                saved_leaf = self._at(i, at_func)

            leaf_func(saved_leaf, leaf_ix, i)

    def for_each(
        self, func: Callable[[T, int], Any], start: int = 0, end: Optional[int] = None,
    ) -> None:
        """Public facing variant of _for_each_leaf. Accepts a callback that's applied
        to each element within the Vector.

        Args:
            func (Callable[[T, int], None]): callback that accepts:
            the current value,
            the current index?.
            start (int): starting position, defaults to 0.
            end (Optional[int]): ending position, defaults to self.length. If end < 0, end += self.length.
        """

        # We wrap the input callback in a leaf_func call,
        # since we only care about the raw child value.
        def leaf_func(leaf: Node[T], leaf_ix: int, ix: int) -> None:
            curr_val = leaf.children[leaf_ix]
            func(cast(T, curr_val), ix)

        return self._for_each_leaf(leaf_func, start, end)

    @overload
    def reduce(
        self,
        func: Callable[[S, T, int], S],
        init: S,
        start: int = 0,
        end: Optional[int] = None,
    ) -> S:
        pass

    @overload
    def reduce(
        self, func: Callable[[T, T, int], T], start: int = 0, end: Optional[int] = None
    ) -> T:
        pass

    def reduce(
        self,
        func: Any,
        init: Optional[Any] = None,
        start: int = 0,
        end: Optional[int] = None,
    ) -> Any:
        if init is None:
            start = 1
            init = self[0]

        acc = init

        def _func(curr_val: T, i: int) -> None:
            nonlocal acc
            acc = func(acc, curr_val, i)

        self.for_each(_func, start, end)

        return acc

    def map(
        self, func: Callable[[T, int], S], start: int = 0, end: Optional[int] = None
    ) -> "Vector[S]":
        out: "Vector[S]" = Vector([])

        out.mutate()

        def _func(curr_val: T, ix: int) -> None:
            out.append(func(curr_val, ix))

        self.for_each(_func, start, end)

        out.mutate()

        return out

    def join(self, separator: str = ",") -> str:
        if len(self) > 0:
            s = self.reduce(lambda s, curr_val, i: f"{s}{separator}{curr_val}", "")
            return s
        else:
            return ""

