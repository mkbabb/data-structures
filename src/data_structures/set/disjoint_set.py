from typing import *
from dataclasses import dataclass

T = TypeVar("T")


@dataclass
class Node:
    id: int
    parent_id: Optional[int]
    child_count: int


class DisjointSet(Generic[T]):
    def __init__(self, *values: T):
        self.data: List[Node] = []
        self.data_map: Dict[int, T] = {}
        self.id = 0

        for value in values:
            self.make_set(value)

    def _get_node(self, value: T) -> Optional[Node]:
        for k, v in self.data_map.items():
            if v == value:
                return self.data[k]
        return None

    def make_set(self, value: T) -> "DisjointSet[T]":
        self.data_map[self.id] = value
        self.data.append(Node(id=self.id, parent_id=None, child_count=1))
        self.id += 1

        return self

    def union(self, a: T, b: T) -> "DisjointSet[T]":
        node_a = self.find(a)
        node_b = self.find(b)

        if node_a is None or node_b is None:
            return self

        if node_a.child_count > node_b.child_count:
            node_a.parent_id = node_b.id
            node_b.child_count += node_a.child_count
        else:
            node_b.parent_id = node_a.id
            node_a.child_count += node_b.child_count

        return self

    def _find(self, node: Node) -> Node:
        if node.parent_id is None:
            return node
        else:
            parent = self._find(self.data[node.parent_id])
            node.parent_id = parent.id
            return parent

    def find(self, value: T) -> Optional[Node]:
        node = self._get_node(value)

        if node is not None:
            return self._find(node)
        else:
            return None

    def get_sets(self) -> Dict[int, List[T]]:
        sets: Dict[int, List[T]] = {}

        for id, value in self.data_map.items():
            parent = self._find(self.data[id])

            if parent.id not in sets:
                sets[parent.id] = []

            if parent.id != id:
                sets[parent.id].append(value)

        return sets


if __name__ == "__main__":
    s = DisjointSet("a", "b", "c", "d", "e", "f")

    s.union("a", "b").union("a", "c").union("a", "f").union("c", "d")

    sets = s.get_sets()
    for parent_id, values in sets.items():
        parent_value = s.data_map[parent_id]
        print(f"{parent_value} : {values}")
