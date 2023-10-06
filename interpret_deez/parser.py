import enum
from dataclasses import dataclass, field
from typing import Callable

from defer.sugarfree import defer

from interpret_deez import ast, lexer, tokenizer
from interpret_deez.parser_tracing import TraceDeez


class Precedences(enum.IntEnum):
    LOWEST = 1
    EQUALS = 2  # ==
    LESS_GREATER = 3  # < OR >
    SUM = 4  # +
    PRODUCT = 5  # *
    PREFIX = 6  # -x OR !x
    CALL = 7  # my_function(x)


precedences = {
    tokenizer.EQ: Precedences.EQUALS,
    tokenizer.NOT_EQ: Precedences.EQUALS,
    tokenizer.LT: Precedences.LESS_GREATER,
    tokenizer.GT: Precedences.LESS_GREATER,
    tokenizer.PLUS: Precedences.SUM,
    tokenizer.MINUS: Precedences.SUM,
    tokenizer.SLASH: Precedences.PRODUCT,
    tokenizer.ASTERISK: Precedences.PRODUCT,
}


@dataclass
class Parser:
    lex: lexer.Lexer
    errors: list = field(default_factory=list)
    prefix_parse_functions: dict[tokenizer.TokenType, Callable[[], ast.Expression | None]] = field(
        init=False
    )
    infix_parse_functions: dict[
        tokenizer.TokenType, Callable[[ast.Expression | None], ast.Expression | None]
    ] = field(init=False)
    enable_defer: bool = field(default=False)

    def __post_init__(self):
        self.current = tokenizer.Token(tokenizer.ILLEGAL, "ILLEGAL")  # avoid type hinting warnings
        self.peek = tokenizer.Token(tokenizer.ILLEGAL, "ILLEGAL")  # avoid type hinting warnings
        self.next_token()
        self.next_token()
        self.errors = []
        self.prefix_parse_functions = {}
        self.infix_parse_functions = {}
        self.register_prefix(tokenizer.IDENT, self.parse_identifier)
        self.register_prefix(tokenizer.INT, self.parse_integer_literal)
        self.register_prefix(tokenizer.BANG, self.parse_prefix_expression)
        self.register_prefix(tokenizer.MINUS, self.parse_prefix_expression)
        self.register_prefix(tokenizer.TRUE, self.parse_boolean)
        self.register_prefix(tokenizer.FALSE, self.parse_boolean)
        self.register_prefix(tokenizer.LPAREN, self.parse_grouped_expression)
        self.register_prefix(tokenizer.IF, self.parse_if_expression)
        self.register_infix(tokenizer.EQ, self.parse_infix_expression)
        self.register_infix(tokenizer.NOT_EQ, self.parse_infix_expression)
        self.register_infix(tokenizer.LT, self.parse_infix_expression)
        self.register_infix(tokenizer.GT, self.parse_infix_expression)
        self.register_infix(tokenizer.PLUS, self.parse_infix_expression)
        self.register_infix(tokenizer.MINUS, self.parse_infix_expression)
        self.register_infix(tokenizer.SLASH, self.parse_infix_expression)
        self.register_infix(tokenizer.ASTERISK, self.parse_infix_expression)
        self.trace_deez = TraceDeez()

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
        if self.enable_defer:
            defer(
                self.trace_deez.end_trace, self.trace_deez.begin_trace("parse_expression_statement")
            )
        statement = ast.ExpressionStatement(self.current)
        statement.expression = self.parse_expression(Precedences.LOWEST)

        if self.is_peek(tokenizer.SEMICOLON):
            self.next_token()

        return statement

    def parse_expression(self, precedence: int) -> ast.Expression | None:
        if self.enable_defer:
            defer(self.trace_deez.end_trace, self.trace_deez.begin_trace("parse_expression"))
        prefix = self.prefix_parse_functions.get(self.current.type)
        if prefix is None:
            self.no_prefix_parse_function_error(self.current.type)
            return None
        left_expression = prefix()

        while not self.is_peek(tokenizer.SEMICOLON) and (precedence < self.peek_precedence()):
            infix = self.infix_parse_functions.get(self.peek.type)
            if infix is None:
                return left_expression

            self.next_token()
            left_expression = infix(left_expression)

        return left_expression

    def parse_identifier(self) -> ast.Expression:
        return ast.Identifier(self.current, self.current.literal)

    def parse_boolean(self) -> ast.Expression:
        return ast.Boolean(self.current, self.is_current(tokenizer.TRUE))

    def parse_grouped_expression(self) -> ast.Expression | None:
        self.next_token()
        expression = self.parse_expression(Precedences.LOWEST)

        if not self.expected_peek(tokenizer.RPAREN):
            return None
        return expression

    def parse_integer_literal(self) -> ast.Expression | None:
        if self.enable_defer:
            defer(self.trace_deez.end_trace, self.trace_deez.begin_trace("parse_integer_literal"))
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
        if self.enable_defer:
            defer(self.trace_deez.end_trace, self.trace_deez.begin_trace("parse_prefix_expression"))
        expression = ast.PrefixExpression(self.current, self.current.literal)
        self.next_token()
        expression.right = self.parse_expression(Precedences.PREFIX)

        return expression

    def parse_infix_expression(self, left: ast.Expression | None) -> ast.Expression:
        if self.enable_defer:
            defer(self.trace_deez.end_trace, self.trace_deez.begin_trace("parse_infix_expression"))
        expression = ast.InfixExpression(self.current, left, self.current.literal)
        precedence = self.current_precedence()
        self.next_token()
        expression.right = self.parse_expression(precedence)

        return expression

    def parse_if_expression(self) -> ast.Expression | None:
        if self.enable_defer:
            defer(self.trace_deez.end_trace, self.trace_deez.begin_trace("parse_if_expression"))
        expression = ast.IfExpression(self.current)

        if not self.expected_peek(tokenizer.LPAREN):
            return None

        self.next_token()
        expression.condition = self.parse_expression(Precedences.LOWEST)

        if not self.expected_peek(tokenizer.RPAREN):
            return None

        if not self.expected_peek(tokenizer.LBRACE):
            return None

        expression.consequence = self.parse_block_statement()

        if self.is_peek(tokenizer.ELSE):
            self.next_token()
            if not self.expected_peek(tokenizer.LBRACE):
                return None
            expression.alternative = self.parse_block_statement()

        return expression

    def parse_block_statement(self) -> ast.BlockStatement:
        block = ast.BlockStatement(self.current)
        block.statements = []
        self.next_token()

        while not self.is_current(tokenizer.RBRACE) and not self.is_current(tokenizer.EOF):
            statement = self.parse_statement()
            if statement is not None:
                block.statements.append(statement)
            self.next_token()

        return block

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
        self,
        token_type: tokenizer.TokenType,
        fn: Callable[[ast.Expression | None], ast.Expression | None],
    ):
        self.infix_parse_functions[token_type] = fn

    def no_prefix_parse_function_error(self, token_type: tokenizer.TokenType):
        message = f"no prefix parse function {token_type} found"
        self.errors.append(message)

    def peek_precedence(self) -> int:
        return (
            Precedences.LOWEST
            if not precedences.get(self.peek.type)
            else precedences[self.peek.type]
        )

    def current_precedence(self) -> int:
        return (
            Precedences.LOWEST
            if not precedences.get(self.current.type)
            else precedences[self.current.type]
        )
