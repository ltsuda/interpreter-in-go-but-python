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

    @abstractmethod
    def to_string(self) -> str:
        """Debugging AST nodes

        Returns:
            str: AST node as string
        """
        ...


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

    def to_string(self) -> str:
        return self.value


@dataclass
class IntegerLiteral(Expression):
    value: int | None = None

    def expression_node(self) -> None:
        ...

    def to_string(self) -> str:
        return self.token.literal


@dataclass
class LetStatement(Statement):
    name: Optional[Identifier] = None
    value: Optional[Expression] = None

    def statement_node(self) -> str:
        ...

    def to_string(self) -> str:
        out = f"{self.token_literal()} {self.name.to_string() if self.name else ''} ="

        if self.value is not None:
            out = f"{out} {self.value.to_string()}"

        out = f"{out};"

        return out


@dataclass
class ReturnStatement(Statement):
    return_value: Optional[Expression] = None

    def statement_node(self) -> str:
        ...

    def to_string(self) -> str:
        out = f"{self.token_literal()}"

        if self.return_value is not None:
            out = f"{out} {self.return_value.to_string()}"

        out = f"{out};"

        return out


@dataclass
class ExpressionStatement(Statement):
    expression: Optional[Expression] = None

    def statement_node(self) -> str:
        ...

    def to_string(self) -> str:
        if self.expression is not None:
            return f"{self.expression.to_string()}"

        return ""


@dataclass
class Program:
    statements: list[Statement] = field(default_factory=list)

    def token_literal(self) -> str:
        if self.statements:
            return self.statements[0].token_literal()  # type: ignore
        return ""

    def to_string(self) -> str:
        out: str = ""
        for statement in self.statements:
            out = f"{statement.to_string()}"

        return out
