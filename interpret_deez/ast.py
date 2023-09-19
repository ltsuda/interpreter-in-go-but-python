from dataclasses import dataclass
from typing import Protocol

from interpret_deez.tokenizer import Token


@dataclass
class Node(Protocol):
    def token_literal(self) -> str:
        """Returns literal value of the token

        Returns:
            str: literal value
        """
        ...


@dataclass
class Statement:
    def token_literal(self) -> str:
        """Returns literal value of the token

        Returns:
            str: literal value
        """
        ...

    def statement_node(self) -> str:
        ...


@dataclass
class Expression:
    def token_literal(self) -> str:
        """Returns literal value of the token

        Returns:
            str: literal value
        """
        ...

    def expression_node(self):
        ...


@dataclass
class Identifier:
    token: Token  # IDENT
    value: str

    def token_literal(self) -> str:
        return self.token.literal

    def expression_node(self) -> None:
        ...


@dataclass
class LetStatement:
    token: Token  # LET
    name: Identifier | None = None
    value: Expression | None = None

    def token_literal(self) -> str:
        """Returns literal value of the token

        Returns:
            str: literal value
        """
        return self.token.literal

    def statement_node(self) -> str:
        ...


@dataclass
class Program:
    statements: list[Statement, LetStatement]

    def token_literal(self) -> str:
        if len(self.statements) > 0:
            return self.statements[0].token_literal()  # type: ignore
        return ""
