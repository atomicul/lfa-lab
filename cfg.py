#!/usr/bin/env python3
from collections.abc import Iterable
from dataclasses import dataclass

LAMBDA_SYMBOL = "$"


@dataclass(frozen=True)
class Production:
    lhs: str
    rhs: tuple[str, ...]

    def __str__(self) -> str:
        body = " ".join(self.rhs) if self.rhs else LAMBDA_SYMBOL
        return f"{self.lhs} -> {body}"


@dataclass
class Grammar:
    non_terminals: set[str]
    terminals: set[str]
    productions: set[Production]
    start: str

    @classmethod
    def from_file(cls, path: str) -> Grammar:
        with open(path, "r") as f:
            non_terminals = set(f.readline().split())
            terminals = set(f.readline().split())
            start = f.readline().strip()

            productions: set[Production] = set()
            for line in f:
                if not line.strip():
                    continue

                lhs, rhs = line.split("->")

                for alternative in rhs.split("|"):
                    symbols = alternative.split()
                    if symbols == [LAMBDA_SYMBOL]:
                        symbols = []
                    productions.add(Production(lhs.strip(), tuple(symbols)))

            return cls(non_terminals, terminals, productions, start)

    def productions_for(self, symbol: str) -> Iterable[Production]:
        return (p for p in self.productions if p.lhs == symbol)

    def shortest_yield(self) -> dict[str, float]:
        shortest: dict[str, float] = {t: 1 for t in self.terminals}
        shortest.update({nt: float("inf") for nt in self.non_terminals})

        while True:
            for p in self.productions:
                candidate = sum(shortest[s] for s in p.rhs)
                if candidate < shortest[p.lhs]:
                    shortest[p.lhs] = candidate
                    break
            else:
                return shortest


    def words_of_length(self, length: int) -> Iterable[str]:
        shortest = self.shortest_yield()

        def min_length(form: tuple[str, ...]) -> float:
            return sum(shortest[s] for s in form)

        start_form = (self.start,)
        visited: set[tuple[str, ...]] = {start_form}
        stack: list[tuple[str, ...]] = [start_form]

        while stack:
            form = stack.pop()

            leftmost = next(
                (i for i, sym in enumerate(form) if sym in self.non_terminals),
                None,
            )

            if leftmost is None:
                if len(form) == length:
                    yield "".join(form)
                continue

            for production in self.productions_for(form[leftmost]):
                expanded = form[:leftmost] + production.rhs + form[leftmost + 1 :]

                if min_length(expanded) <= length and expanded not in visited:
                    visited.add(expanded)
                    stack.append(expanded)

    def __str__(self) -> str:
        ordered = [self.start, *sorted(self.non_terminals - {self.start})]

        lines = [
            " ".join(ordered),
            " ".join(sorted(self.terminals)),
            self.start,
        ]

        for symbol in ordered:
            alternatives = sorted(self.productions_for(symbol), key=lambda p: p.rhs)
            if not alternatives:
                continue

            body = " | ".join(
                " ".join(p.rhs) if p.rhs else LAMBDA_SYMBOL for p in alternatives
            )
            lines.append(f"{symbol} -> {body}")

        return "\n".join(lines)


def main():
    grammar = Grammar.from_file("cfg.txt")

    try:
        while True:
            length = int(input())
            for word in sorted(grammar.words_of_length(length)):
                print(word)
    except EOFError:
        pass


if __name__ == "__main__":
    main()
