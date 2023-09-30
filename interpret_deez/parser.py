from dataclasses import dataclass, field

from interpret_deez import ast, lexer, tokenizer


@dataclass
class Parser:
    lex: lexer.Lexer
    errors: list = field(default_factory=list)

    def __post_init__(self):
        self.current = tokenizer.Token(tokenizer.ILLEGAL, "ILLEGAL")  # avoid type hinting warnings
        self.peek = tokenizer.Token(tokenizer.ILLEGAL, "ILLEGAL")  # avoid type hinting warnings
        self.next_token()
        self.next_token()
        self.errors = []

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
                return None

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
