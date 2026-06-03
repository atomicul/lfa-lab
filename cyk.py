#!/usr/bin/env python3
import functools
from collections import defaultdict
from cfg import Grammar
from chomsky_normal_form import to_cnf


def cyk(grammar: Grammar, word: str) -> bool:
    if not word:
        return any(p.lhs == grammar.start and not p.rhs for p in grammar.productions)

    terminal_rules: dict[str, set[str]] = defaultdict(set)
    binary_rules: dict[tuple[str, str], set[str]] = defaultdict(set)
    for p in grammar.productions:
        if len(p.rhs) == 1 and p.rhs[0] in grammar.terminals:
            terminal_rules[p.rhs[0]].add(p.lhs)
        elif len(p.rhs) == 2:
            binary_rules[p.rhs[0], p.rhs[1]].add(p.lhs)

    @functools.cache
    def derive(start: int, length: int) -> frozenset[str]:
        if length == 1:
            return frozenset(terminal_rules.get(word[start], ()))
        return frozenset(
            a
            for split in range(1, length)
            for b in derive(start, split)
            for c in derive(start + split, length - split)
            for a in binary_rules.get((b, c), ())
        )

    return grammar.start in derive(0, len(word))


def main():
    grammar = to_cnf(Grammar.from_file("cfg.txt"))

    try:
        while True:
            word = input()
            print("DA" if cyk(grammar, word) else "NU")
    except EOFError:
        pass


if __name__ == "__main__":
    main()
