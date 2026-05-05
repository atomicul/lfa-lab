#!/usr/bin/env python3


def main():
    initial_node, final_nodes = read_dfa()

    try:
        while True:
            word = input()

            state = initial_node.check(word)

            if state is None:
                print("Error: invalid state reached for word", word)

            print("VALID" if state in final_nodes else "INVALID")

    except EOFError:
        pass


class Node:
    transitions: dict[str, Node]

    def __init__(self) -> None:
        self.transitions = dict()

    def check(self, word: str) -> Node | None:
        if not word:
            return self

        x, *xs = word
        xs = "".join(xs)

        n = self.transitions.get(x, None)

        if n is None:
            return None

        return n.check(xs)


def read_dfa() -> tuple[Node, list[Node]]:
    with open("dfa.txt", "r") as f:
        node_count = int(f.readline())
        nodes = [Node() for _ in range(node_count)]
        initial_node = nodes[int(f.readline()) - 1]
        final_nodes = [nodes[x - 1] for x in map(int, f.readline().split())]

        for line in f.readlines():
            src, letter, dest = line.split()
            src = int(src) - 1
            dest = int(dest) - 1

            nodes[src].transitions[letter] = nodes[dest]

        return (initial_node, final_nodes)


if __name__ == "__main__":
    main()
