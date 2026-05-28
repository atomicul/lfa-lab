#!/usr/bin/env python3
from collections.abc import Iterable
from dataclasses import dataclass
from typing import NamedTuple
import enum

LAMBDA_SYMBOL = "$"
BOTTOM_OF_STACK = ord("Z")


type Stack = StackValue | None


class StackValue(NamedTuple):
    letter: int
    tail: Stack


class AcceptMode(enum.Flag):
    EMPTY_STACK = enum.auto()
    END_STATE = enum.auto()


@dataclass(frozen=True)
class Transition:
    letter: int | None
    precondition: int
    replacement: bytes
    destination: State


class State:
    __name: str
    transitions: set[Transition]

    @property
    def name(self) -> str:
        return self.__name

    def __init__(self, name: str):
        self.__name = name
        self.transitions = set()

    def __eq__(self, other):
        if not isinstance(other, State):
            return NotImplemented
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return f"{type(self).__name__}({self.name!r})"


class PDA:
    __states: set[State]
    __begin_state: State
    __end_states: set[State]
    __accept_mode: AcceptMode

    def __init__(
        self,
        states: Iterable[State],
        *,
        begin_state: State,
        end_states: Iterable[State] = (),
        accept_mode: AcceptMode = AcceptMode.END_STATE | AcceptMode.EMPTY_STACK,
    ):
        self.__states = set(states)
        self.__begin_state = begin_state
        self.__end_states = set(end_states)
        self.__accept_mode = accept_mode

    @classmethod
    def from_file(cls, path: str) -> PDA:
        with open(path, "r") as f:
            state_count = int(f.readline())
            states = [State(f"q{i}") for i in range(state_count)]
            begin_state = states[int(f.readline()) - 1]
            end_states = [states[i - 1] for i in map(int, f.readline().split())]

            for line in f:
                if not line.strip():
                    continue

                src, letter, pop, push, dest = line.split()

                states[int(src) - 1].transitions.add(
                    Transition(
                        letter=None if letter == LAMBDA_SYMBOL else ord(letter),
                        precondition=ord(pop),
                        replacement=b""
                        if push == LAMBDA_SYMBOL
                        else push.encode("ascii"),
                        destination=states[int(dest) - 1],
                    )
                )

            return cls(states, begin_state=begin_state, end_states=end_states)

    def accept(self, word: str) -> bool:
        visited: set[tuple[State, memoryview, Stack]] = set()

        def recurse(state: State, word: memoryview, stack: Stack) -> bool:
            key = (state, word, stack)
            if key in visited:
                return False
            visited.add(key)

            def is_end_state() -> bool:
                if word:
                    return False

                if (
                    self.__accept_mode & AcceptMode.END_STATE
                    and state not in self.__end_states
                ):
                    return False

                if self.__accept_mode & AcceptMode.EMPTY_STACK and stack:
                    return False

                return True

            if is_end_state():
                return True

            if not stack:
                return False

            top, stack = stack

            valid_transitions = [t for t in state.transitions if t.precondition == top]

            next_states: list[tuple[State, memoryview, bytes]] = []
            next_states.extend(
                (t.destination, word, t.replacement)
                for t in valid_transitions
                if t.letter is None
            )
            next_states.extend(
                (t.destination, word[1:], t.replacement)
                for t in valid_transitions
                if t.letter is not None and word and t.letter == word[0]
            )

            def backtracking_branches() -> Iterable[bool]:
                for next_state, next_word, stack_replacement in next_states:
                    new_stack: Stack = stack
                    for char in reversed(stack_replacement):
                        new_stack = StackValue(char, new_stack)

                    yield recurse(next_state, next_word, new_stack)

            return any(backtracking_branches())

        return recurse(
            self.__begin_state,
            memoryview(word.encode("ascii")),
            StackValue(BOTTOM_OF_STACK, None),
        )

    def __repr__(self):
        return f"{type(self).__name__}(states={self.__states!r}, begin_state={self.__begin_state!r}, end_states={self.__end_states!r}, accept_mode={self.__accept_mode!r})"


def main():
    pda = PDA.from_file("pda.txt")

    try:
        while True:
            word = input()
            print("VALID" if pda.accept(word) else "INVALID")
    except EOFError:
        pass


if __name__ == "__main__":
    main()
