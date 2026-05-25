#!/usr/bin/env python3

from collections.abc import Iterable
import itertools
import operator
from lambda_nfa import read_nfa, Node, LAMBDA_SYMBOL


def main():
    start_node, end_nodes = read_nfa()

    nodes = set(discover_nodes(start_node))
    mapping = join_transitions(nodes)

    START_PSEUDO_NODE = Node()
    END_PSEUDO_NODE = Node()

    mapping[START_PSEUDO_NODE, start_node] = ""
    for end_node in end_nodes:
        mapping[end_node, END_PSEUDO_NODE] = ""

    def expanded_node_list():
        return nodes | {START_PSEUDO_NODE, END_PSEUDO_NODE}

    while nodes:
        node = nodes.pop()

        outgoing_neighbours = {
            n for n in expanded_node_list() if n is not node and (node, n) in mapping
        }
        incoming_neighbours = {
            n for n in expanded_node_list() if n is not node and (n, node) in mapping
        }

        for i, j in itertools.product(incoming_neighbours, outgoing_neighbours):
            parts = []

            if mapping.get((i, j), ""):
                parts.append(mapping[i, j])

            regex = ""

            regex += mapping[i, node]
            if mapping.get((node, node), ""):
                expr = mapping[node, node]
                if len(expr) > 1:
                    expr = f"({expr})"
                regex += expr + "*"

            regex += mapping[node, j]

            parts.append(regex)

            mapping[i, j] = or_group(parts)

    print(mapping[START_PSEUDO_NODE, END_PSEUDO_NODE].strip("()"))


def join_transitions(nodes: Iterable[Node]) -> dict[tuple[Node, Node], str]:
    out: dict[tuple[Node, Node], str] = {}
    for n1, n2 in itertools.product(nodes, nodes):
        to_n2 = [
            symbol
            for symbol, target in n1.transitions
            if target is n2 and symbol != LAMBDA_SYMBOL
        ]

        match to_n2:
            case []:
                if (LAMBDA_SYMBOL, n2) in n1.transitions:
                    out[n1, n2] = ""
            case [symbol]:
                out[n1, n2] = symbol
            case [*_]:
                out[n1, n2] = or_group(sorted(to_n2))

    return out


def discover_nodes(
    node: Node, /, *, visited: set[Node] | None = None
) -> Iterable[Node]:
    if visited is None:
        visited = set()

    if node in visited:
        return
    visited.add(node)

    yield node

    for n in map(operator.itemgetter(1), node.transitions):
        yield from discover_nodes(n, visited=visited)


def or_group(exprs: Iterable[str]):
    first, *other = exprs

    if not other:
        return first

    return "({})".format("|".join([first] + other))


if __name__ == "__main__":
    main()
