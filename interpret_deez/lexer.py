import re
from dataclasses import dataclass

from interpret_deez import tokenizer

is_letter_rexp = re.compile("[a-zA-Z_]")
is_digit_rexp = re.compile("[0-9]")


@dataclass
class Lexer:
    inp: str
    position = 0
    read_position = 0
    char = 0

    def __post_init__(self):
        self.read_char()

    def read_char(self) -> None:
        if self.read_position >= len(self.inp):
            self.char = 0
        else:
            self.char = self.inp[self.read_position]
        self.position = self.read_position
        self.read_position += 1

    def new_token(self, token_type: tokenizer.TokenType, char) -> tokenizer.Token:
        return tokenizer.Token(type=token_type, literal=str(char))

    def next_token(self) -> tokenizer.Token:
        _token: tokenizer.Token

        self.skip_whitespace()

        match self.char:
            case "=":
                if self.peek_char() == "=":
                    char = self.char
                    self.read_char()
                    literal = f"{char}{self.char}"
                    _token = self.new_token(tokenizer.EQ, literal)
                else:
                    _token = self.new_token(tokenizer.ASSIGN, self.char)
            case ";":
                _token = self.new_token(tokenizer.SEMICOLON, self.char)
            case "(":
                _token = self.new_token(tokenizer.LPAREN, self.char)
            case ")":
                _token = self.new_token(tokenizer.RPAREN, self.char)
            case ",":
                _token = self.new_token(tokenizer.COMMA, self.char)
            case "+":
                _token = self.new_token(tokenizer.PLUS, self.char)
            case "-":
                _token = self.new_token(tokenizer.MINUS, self.char)
            case "!":
                if self.peek_char() == "=":
                    char = self.char
                    self.read_char()
                    literal = f"{char}{self.char}"
                    _token = self.new_token(tokenizer.NOT_EQ, literal)
                else:
                    _token = self.new_token(tokenizer.BANG, self.char)
            case "/":
                _token = self.new_token(tokenizer.SLASH, self.char)
            case "*":
                _token = self.new_token(tokenizer.ASTERISK, self.char)
            case "<":
                _token = self.new_token(tokenizer.LT, self.char)
            case ">":
                _token = self.new_token(tokenizer.GT, self.char)
            case "{":
                _token = self.new_token(tokenizer.LBRACE, self.char)
            case "}":
                _token = self.new_token(tokenizer.RBRACE, self.char)
            case 0:
                _token = self.new_token(tokenizer.EOF, "")
            case _:
                if self.is_letter(self.char):
                    ident = self.read_identifier()
                    return self.new_token(tokenizer.lookup_identfier(ident), ident)
                elif self.is_digit(self.char):
                    return self.new_token(tokenizer.INT, self.read_number())
                _token = self.new_token(tokenizer.ILLEGAL, self.char)
        self.read_char()
        return _token

    def is_letter(self, char) -> bool:
        return re.fullmatch(is_letter_rexp, char) is not None

    def is_digit(self, char) -> bool:
        return re.fullmatch(is_digit_rexp, char) is not None

    def read_identifier(self) -> str:
        position = self.position
        while self.is_letter(self.char):
            self.read_char()
        return self.inp[position : self.position]

    def read_number(self) -> str:
        position = self.position
        while self.is_digit(self.char):
            self.read_char()
        return self.inp[position : self.position]

    def skip_whitespace(self) -> None:
        while self.char == " " or self.char == "\t" or self.char == "\n" or self.char == "\r":
            self.read_char()

    def peek_char(self) -> int | str:
        if self.read_position >= len(self.inp):
            return 0
        return self.inp[self.read_position]
