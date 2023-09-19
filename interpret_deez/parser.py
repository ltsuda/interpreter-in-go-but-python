from dataclasses import dataclass

from interpret_deez import ast, lexer, tokenizer


@dataclass
class Parser:
    lex: lexer.Lexer

    def __post_init__(self):
        self.current = tokenizer.Token(tokenizer.ILLEGAL, "ILLEGAL")  # avoid type hinting warnings
        self.peek = tokenizer.Token(tokenizer.ILLEGAL, "ILLEGAL")  # avoid type hinting warnings
        self.next_token()
        self.next_token()

    def next_token(self) -> None:
        self.current = self.peek
        self.peek = self.lex.next_token()

    def parse_program(self) -> ast.Program:
        program = ast.Program()

        while self.current.type != tokenizer.EOF:
            statement = self.parse_statement()
            if statement:
                program.statements.append(statement)
            self.next_token()
        return program

    def parse_statement(self) -> ast.Statement | None:
        match self.current.type:
            case tokenizer.LET:
                return self.parse_let_statement()
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

    def is_current(self, token_type: tokenizer.TokenType) -> bool:
        return self.current.type == token_type

    def is_peek(self, token_type: tokenizer.TokenType) -> bool:
        return self.peek.type == token_type

    def expected_peek(self, token_type: tokenizer.TokenType) -> bool:
        if self.is_peek(token_type):
            self.next_token()
            return True
        else:
            return False
