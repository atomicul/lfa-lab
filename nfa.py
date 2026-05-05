#!/usr/bin/env python3

from collections.abc import Iterable
from collections import deque


def main():
    initial_node, final_nodes = read_nfa()
    final_nodes = set(final_nodes)

    try:
        while True:
            word = input()

            state = set(initial_node.check(word))

            print("VALID" if (state & final_nodes) else "INVALID")

    except EOFError:
        pass


class Node:
    transitions: list[tuple[str, Node]]

    def __init__(self) -> None:
        self.transitions = []

    def check(self, word: str) -> Iterable[Node]:
        q: deque[tuple[Node, str]] = deque()
        q.append((self, word))

        while q:
            node, word = q.popleft()

            if not word:
                yield node
                continue

            x, *xs = word
            xs = "".join(xs)

            nodes = [n for k, n in node.transitions if k == x]

            for n in nodes:
                q.append((n, xs))


def read_nfa() -> tuple[Node, list[Node]]:
    with open("nfa.txt", "r") as f:
        node_count = int(f.readline())
        nodes = [Node() for _ in range(node_count)]
        initial_node = nodes[int(f.readline()) - 1]
        final_nodes = [nodes[x - 1] for x in map(int, f.readline().split())]

        for line in f.readlines():
            src, letter, dest = line.split()
            src = int(src) - 1
            dest = int(dest) - 1

            nodes[src].transitions.append((letter, nodes[dest]))

        return (initial_node, final_nodes)


if __name__ == "__main__":
    main()
