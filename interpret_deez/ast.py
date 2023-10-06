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
class PrefixExpression(Expression):
    operator: str
    right: Expression | None = None

    def expression_node(self) -> None:
        ...

    def to_string(self) -> str:
        return f"({self.operator}{self.right.to_string() if self.right else ''})"


@dataclass
class InfixExpression(Expression):
    left: Expression | None
    operator: str
    right: Expression | None = None

    def expression_node(self) -> None:
        ...

    def to_string(self) -> str:
        out = f"{self.left.to_string() if self.left else ''}"
        out = f"{out} {self.operator}"
        out = f"({out} {self.right.to_string() if self.right else ''})"
        return out


@dataclass
class BlockStatement(Statement):
    statements: list[Statement] = field(default_factory=list)

    def statement_node(self) -> None:
        ...

    def to_string(self) -> str:
        return "".join(statement.to_string() for statement in self.statements)


@dataclass
class IfExpression(Expression):
    condition: Optional[Expression] = None
    consequence: Optional[BlockStatement] = None
    alternative: Optional[BlockStatement] = None

    def expression_node(self) -> None:
        ...

    def to_string(self) -> str:
        out = "if"
        out = f"{out}{self.condition.to_string() if self.condition else ''} "
        out = f"{out}{self.consequence.to_string() if self.consequence else ''}"

        if self.alternative is not None:
            out = f"{out}else "
            out = f"{out}{self.alternative.to_string() if self.alternative else ''}"
        return out


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
class FunctionLiteral(Expression):
    parameters: list[Identifier] | None = field(default_factory=list)  # noqa: F811
    body: Optional[BlockStatement] = None

    def expression_node(self) -> None:
        ...

    def to_string(self) -> str:
        params = "".join(parameter.to_string() for parameter in self.parameters)  # type: ignore

        out = (
            f"{self.token_literal()}({', '.join(params)}) "
            f"{self.body.to_string() if self.body else ''}"
        )
        return out


@dataclass
class Boolean(Expression):
    value: bool | None = None

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
            return self.expression.to_string()

        return ""


@dataclass
class Program:
    statements: list[Statement] = field(default_factory=list)

    def token_literal(self) -> str:
        if self.statements:
            return self.statements[0].token_literal()
        return ""

    def to_string(self) -> str:
        return "".join(statement.to_string() for statement in self.statements)
