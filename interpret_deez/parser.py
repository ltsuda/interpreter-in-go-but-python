from dataclasses import dataclass, field
import enum
from typing import Callable

from interpret_deez import ast, lexer, tokenizer


def prefix_parse_function() -> ast.Expression:
    ...


def infix_parse_function(expression: ast.Expression) -> ast.Expression:
    ...


class Precedences(enum.IntEnum):
    LOWEST = 1
    EQUALS = 2  # ==
    LESS_GREATER = 3  # < OR >
    SUM = 4  # +
    PRODUCT = 5  # *
    PREFIX = 6  # -x OR !x
    CALL = 7  # my_function(x)


@dataclass
class Parser:
    lex: lexer.Lexer
    errors: list = field(default_factory=list)
    prefix_parse_functions: dict[tokenizer.TokenType, Callable[[], ast.Expression | None]] = field(
        init=False
    )
    infix_parse_functions: dict[
        tokenizer.TokenType, Callable[[ast.Expression], ast.Expression]
    ] = field(init=False)

    def __post_init__(self):
        self.current = tokenizer.Token(tokenizer.ILLEGAL, "ILLEGAL")  # avoid type hinting warnings
        self.peek = tokenizer.Token(tokenizer.ILLEGAL, "ILLEGAL")  # avoid type hinting warnings
        self.next_token()
        self.next_token()
        self.errors = []
        self.prefix_parse_functions = {}
        self.register_prefix(tokenizer.IDENT, self.parse_identifier)
        self.register_prefix(tokenizer.INT, self.parse_integer_literal)
        self.register_prefix(tokenizer.BANG, self.parse_prefix_expression)
        self.register_prefix(tokenizer.MINUS, self.parse_prefix_expression)

    def next_token(self) -> None:
        self.current = self.peek
        self.peek = self.lex.next_token()

    def parse_program(self) -> ast.Program:
        program = ast.Program()

        while not self.is_current(tokenizer.EOF):
            statement = self.parse_statement()
            if statement:
                program.statements.append(statement)
            self.next_token()
        return program

    def parse_statement(self) -> ast.Statement | None:
        match self.current.type:
            case tokenizer.LET:
                return self.parse_let_statement()
            case tokenizer.RETURN:
                return self.parse_return_statement()
            case _:
                return self.parse_expression_statement()

    def parse_let_statement(self) -> ast.LetStatement | None:
        statement = ast.LetStatement(self.current)
        if not self.expected_peek(tokenizer.IDENT):
            return None

        statement.name = ast.Identifier(self.current, self.current.literal)

        if not self.expected_peek(tokenizer.ASSIGN):
            return None

        # TODO: skip expression until encounter a semicolon
        while not self.is_current(tokenizer.SEMICOLON):
            self.next_token()

        return statement

    def parse_return_statement(self) -> ast.ReturnStatement | None:
        statement = ast.ReturnStatement(self.current)
        self.next_token()

        # TODO: We're skipping the expression until we encounter a semicolon
        while not self.is_current(tokenizer.SEMICOLON):
            self.next_token()
        return statement

    def parse_expression_statement(self) -> ast.ExpressionStatement | None:
        statement = ast.ExpressionStatement(self.current)
        statement.expression = self.parse_expression(Precedences.LOWEST)

        if self.expected_peek(tokenizer.SEMICOLON):
            self.next_token()

        return statement

    def parse_expression(self, precedence) -> ast.Expression | None:
        prefix = self.prefix_parse_functions[self.current.type]
        if prefix is None:
            self.no_prefix_parse_function_error(self.current.type)
            return None
        left_expression = prefix()
        return left_expression

    def parse_identifier(self) -> ast.Expression:
        return ast.Identifier(self.current, self.current.literal)

    def parse_integer_literal(self) -> ast.Expression | None:
        integer_literal = ast.IntegerLiteral(self.current)

        try:
            integer_value = int(self.current.literal)
        except ValueError:
            message = f"could not parse {self.current.literal} as int"
            self.errors.extend(message)
            return None

        integer_literal.value = integer_value
        return integer_literal

    def parse_prefix_expression(self) -> ast.Expression:
        expression = ast.PrefixExpression(self.current, self.current.literal)
        self.next_token()
        expression.right = self.parse_expression(Precedences.PREFIX)

        return expression

    def is_current(self, token_type: tokenizer.TokenType) -> bool:
        return self.current.type == token_type

    def is_peek(self, token_type: tokenizer.TokenType) -> bool:
        return self.peek.type == token_type

    def expected_peek(self, token_type: tokenizer.TokenType) -> bool:
        if self.is_peek(token_type):
            self.next_token()
            return True
        else:
            self.peek_errors(token_type)
            return False

    def peek_errors(self, token_type: tokenizer.TokenType) -> None:
        message = f"expected next token to be '{token_type}', got '{self.peek.type}' instead"
        self.errors.extend([message])

    def get_errors(self) -> list[str]:
        return self.errors.copy()

    def register_prefix(
        self, token_type: tokenizer.TokenType, fn: Callable[[], ast.Expression | None]
    ):
        self.prefix_parse_functions[token_type] = fn

    def register_infix(
        self, token_type: tokenizer.TokenType, fn: Callable[[ast.Expression], ast.Expression]
    ):
        self.infix_parse_functions[token_type] = fn

    def no_prefix_parse_function_error(self, token_type: tokenizer.TokenType):
        message = f"no prefix parse function {token_type} found"
        self.errors.extend(message)
