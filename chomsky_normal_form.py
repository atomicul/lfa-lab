#!/usr/bin/env python3
import itertools
import functools
from collections import defaultdict
from cfg import Grammar, Production


def to_cnf(grammar: Grammar) -> Grammar:
    for step in (start_step, term_step, bin_step, del_step, unit_step):
        grammar = step(grammar)
    return grammar


def fresh_name(base: str, taken: set[str]) -> str:
    name = base
    while name in taken:
        name += "'"
    return name


def start_step(grammar: Grammar) -> Grammar:
    if not any(grammar.start in p.rhs for p in grammar.productions):
        return grammar

    new_start = fresh_name(grammar.start + "0", grammar.non_terminals)

    return Grammar(
        non_terminals=grammar.non_terminals | {new_start},
        terminals=grammar.terminals,
        productions=grammar.productions | {Production(new_start, (grammar.start,))},
        start=new_start,
    )


def term_step(grammar: Grammar) -> Grammar:
    non_terminals = set(grammar.non_terminals)
    productions: set[Production] = set()

    @functools.cache
    def variable_for(terminal: str) -> str:
        name = fresh_name(f"T_{terminal}", non_terminals)
        non_terminals.add(name)
        productions.add(Production(name, (terminal,)))
        return name

    for p in grammar.productions:
        if len(p.rhs) < 2:
            productions.add(p)
            continue

        productions.add(
            Production(
                p.lhs,
                tuple(
                    variable_for(sym) if sym in grammar.terminals else sym
                    for sym in p.rhs
                ),
            )
        )

    return Grammar(non_terminals, grammar.terminals, productions, grammar.start)


def bin_step(grammar: Grammar) -> Grammar:
    non_terminals = set(grammar.non_terminals)
    productions: set[Production] = set()
    counter = itertools.count(1)

    for p in grammar.productions:
        if len(p.rhs) <= 2:
            productions.add(p)
            continue

        lhs = p.lhs
        first, *rest = p.rhs
        while len(rest) > 1:
            tail = fresh_name(f"{p.lhs}_{next(counter)}", non_terminals)
            non_terminals.add(tail)
            productions.add(Production(lhs, (first, tail)))
            lhs = tail
            first, *rest = rest

        productions.add(Production(lhs, (first, *rest)))

    return Grammar(non_terminals, grammar.terminals, productions, grammar.start)


def nullable_symbols(grammar: Grammar) -> set[str]:
    nullable: set[str] = set()

    while True:
        for p in grammar.productions:
            if p.lhs not in nullable and all(s in nullable for s in p.rhs):
                nullable.add(p.lhs)
                break
        else:
            return nullable


def del_step(grammar: Grammar) -> Grammar:
    nullable = nullable_symbols(grammar)
    productions: set[Production] = set()

    for p in grammar.productions:
        if not p.rhs:
            continue
        productions.add(p)

        if len(p.rhs) < 2:
            continue
        for i, s in enumerate(p.rhs):
            if s in nullable:
                productions.add(Production(p.lhs, p.rhs[:i] + p.rhs[i + 1 :]))

    if grammar.start in nullable:
        productions.add(Production(grammar.start, ()))

    return Grammar(
        set(grammar.non_terminals), grammar.terminals, productions, grammar.start
    )


def unit_step(grammar: Grammar) -> Grammar:
    def is_unit(p: Production) -> bool:
        return len(p.rhs) == 1 and p.rhs[0] in grammar.non_terminals

    unit_targets: dict[str, set[str]] = defaultdict(set)
    non_unit: dict[str, set[tuple[str, ...]]] = defaultdict(set)
    for p in grammar.productions:
        if is_unit(p):
            unit_targets[p.lhs].add(p.rhs[0])
        else:
            non_unit[p.lhs].add(p.rhs)

    def reachable(start: str) -> set[str]:
        seen, stack = {start}, [start]
        while stack:
            for nxt in unit_targets[stack.pop()] - seen:
                seen.add(nxt)
                stack.append(nxt)
        return seen

    productions = {
        Production(a, rhs)
        for a in grammar.non_terminals
        for b in reachable(a)
        for rhs in non_unit[b]
    }

    return Grammar(
        set(grammar.non_terminals), grammar.terminals, productions, grammar.start
    )


def main():
    print(to_cnf(Grammar.from_file("cfg.txt")))


if __name__ == "__main__":
    main()
