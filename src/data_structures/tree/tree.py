from typing import *

from src.data_structures.utils.utils import Comparator, bisect, default_comparator
from src.data_structures.list.vector import Vector


T = TypeVar("T")


class TreeNode(Generic[T]):
    def __init__(
        self,
        tree_order: int,
        children: Optional[Union[Vector["TreeNode[T]"], List["TreeNode[T]"]]] = None,
        values: Optional[Union[Vector[T], List[T]]] = None,
        parent: Optional["TreeNode[T]"] = None,
    ) -> None:
        self.tree_order = tree_order

        self.parent = parent

        self._children = [] if children is None else children
        self._values = [] if values is None else values

        for child in filter(lambda x: x is not None, self.children):
            child.parent = self

    @property
    def children(self) -> List["TreeNode[T]"]:
        return self._children

    @children.setter
    def children(self, other: List["TreeNode[T]"]) -> None:
        self._children = other

    @property
    def values(self) -> List[T]:
        return self._values

    @values.setter
    def values(self, other: List[T]) -> None:
        self._values = other

    def __repr__(self) -> str:
        return f"{self.values}"

    def order(self) -> int:
        return len(self.values)

    def is_leaf(self) -> bool:
        return len(self.children) == 0

    def is_internal(self) -> bool:
        return not (self.is_root() or self.is_leaf())

    def is_root(self) -> bool:
        return self.parent is None

    def is_full(self) -> bool:
        return len(self.values) >= self.tree_order

    def is_empty(self) -> bool:
        return len(self.values) == 0

    def siblings(
        self, parent_ix: int
    ) -> Tuple[Optional["TreeNode[T]"], Optional["TreeNode[T]"]]:
        def get_child(ix: int) -> Optional["TreeNode[T]"]:
            if self.parent is not None:
                if ix >= 0 and ix < len(self.parent.children):
                    return self.parent.children[ix]
            return None

        left_ix = parent_ix - 1
        right_ix = parent_ix + 1

        return get_child(left_ix), get_child(right_ix)


class Tree(Generic[T]):
    def __init__(self, order: int, comparator: Comparator = default_comparator):
        self.order = order
        self.comparator = comparator
        self.root: TreeNode[T] = self._create_node(tree_order=order)

    def __repr__(self) -> str:
        return str(self.root)

    def _create_node(self, **kwargs: Any) -> TreeNode[T]:
        return TreeNode(**kwargs)

    def _bisect(
        self, arr: List[T], x: T, left: bool = True, negate_found: bool = False
    ) -> int:
        return bisect(arr, x, self.comparator, left, negate_found)

    def _get_node_ix(
        self, node: TreeNode[T], value: T, left: bool = True, negate_found: bool = False
    ):
        return self._bisect(node.values, value, left, negate_found)

    def find(self, input_value: T) -> Tuple[int, TreeNode[T]]:
        def recurse(node: TreeNode[T]) -> Tuple[int, TreeNode[T]]:
            if (ix := self._get_node_ix(node, input_value, negate_found=True)) < 0:
                ix = -1 * (ix + 1)
                if node.is_leaf() or (child := node.children[ix]) is None:
                    return ix, node
                else:
                    return recurse(child)
            else:
                return ix, node

        return recurse(self.root)

    @staticmethod
    def successor(ix: int, node: TreeNode[T]) -> TreeNode[T]:
        if node.is_leaf():
            return node
        else:
            child = node.children[ix + 1]
            while not child.is_leaf():
                child = child.children[0]
            return child

    def _delete(self, input_value: T):
        value_ix, node = self.find(input_value)

        if node.is_leaf():
            child_ix = (
                self._get_node_ix(node.parent, input_value) if not node.is_root() else 0
            )
            return child_ix, node, node.values.pop(value_ix)
        else:
            successor = Tree.successor(value_ix, node)
            value = successor.values[0]
            child_ix = self._get_node_ix(successor.parent, value)

            node.values[value_ix] = value
            return child_ix, successor, successor.values.pop(0)

    def _on_delete(self, child_ix: int, node: TreeNode[T], value: T) -> None:
        pass

    def delete(self, input_value: T) -> T:
        child_ix, node, value = self._delete(input_value)
        self._on_delete(child_ix, node, value)

        return value

    def _on_insert(self, input_value: T, value_ix: int, node: TreeNode[T]) -> None:
        node.values.insert(value_ix, input_value)

    def _insert(self, input_value: T) -> None:
        value_ix, node = self.find(input_value)

        self._on_insert(input_value, value_ix, node)

    def insert(self, *input_values: T) -> None:
        for input_value in input_values:
            self._insert(input_value)

    def in_order(self) -> Iterator[T]:
        def recurse(node: TreeNode[T]) -> Iterator[T]:
            if not node.is_leaf():
                for n, child in enumerate(node.children):
                    recurse(child)

                    if n < len(node.values):
                        yield node.values[n]

            else:
                for value in node.values:
                    yield value

        return recurse(self.root)

    def for_each(self, func: Callable[[T], None]) -> None:
        for value in self.in_order():
            func(value)

    def _print(self):
        def recurse(node: TreeNode[T], s: str, depth: int = 0):
            if not node.is_leaf():
                t_indent = ("|" + "----" * (depth + 1)) if depth > 0 else ""
                for n, child in enumerate(node.children):

                    s = recurse(child, s, depth + 1)

                    if n < len(node.values):
                        s += t_indent + str(node.values[n]) + "\n"
            else:
                spaces = "    " * depth
                t_indent = spaces + "|---" if depth > 0 else ""

                for value in node.values:
                    s += "|" + t_indent + str(value) + ",\n"
            return s

        return recurse(self.root, "")
