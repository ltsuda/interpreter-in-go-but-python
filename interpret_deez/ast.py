from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

from interpret_deez.tokenizer import Token


@dataclass
class Node(ABC):
    token: Token

    def token_literal(self) -> str:
        """Returns literal value of the token

        Returns:
            str: literal value
        """
        return self.token.literal


@dataclass
class Statement(Node):
    @abstractmethod
    def statement_node(self) -> None:
        ...


@dataclass
class Expression(Node):
    @abstractmethod
    def expression_node(self):
        ...


@dataclass
class Identifier(Expression):
    value: str

    def expression_node(self) -> None:
        ...


@dataclass
class LetStatement(Statement):
    name: Optional[Identifier] = None
    value: Optional[Expression] = None

    def statement_node(self) -> str:
        ...


@dataclass
class ReturnStatement(Statement):
    return_value: Optional[Expression] = None

    def statement_node(self) -> str:
        ...


@dataclass
class Program:
    statements: list[Statement] = field(default_factory=list)

    def token_literal(self) -> str:
        if self.statements:
            return self.statements[0].token_literal()  # type: ignore
        return ""
