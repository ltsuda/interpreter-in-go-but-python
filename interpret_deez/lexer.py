import re
from dataclasses import dataclass

from interpret_deez import token

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

    def new_token(self, token_type: token.TokenType, char) -> token.Token:
        return token.Token(type=token_type, literal=str(char))

    def next_token(self) -> token.Token:
        _token: token.Token

        self.skip_whitespace()

        match self.char:
            case "=":
                if self.peek_char() == "=":
                    char = self.char
                    self.read_char()
                    literal = f"{char}{self.char}"
                    _token = self.new_token(token.EQ, literal)
                else:
                    _token = self.new_token(token.ASSIGN, self.char)
            case ";":
                _token = self.new_token(token.SEMICOLON, self.char)
            case "(":
                _token = self.new_token(token.LPAREN, self.char)
            case ")":
                _token = self.new_token(token.RPAREN, self.char)
            case ",":
                _token = self.new_token(token.COMMA, self.char)
            case "+":
                _token = self.new_token(token.PLUS, self.char)
            case "-":
                _token = self.new_token(token.MINUS, self.char)
            case "!":
                if self.peek_char() == "=":
                    char = self.char
                    self.read_char()
                    literal = f"{char}{self.char}"
                    _token = self.new_token(token.NOT_EQ, literal)
                else:
                    _token = self.new_token(token.BANG, self.char)
            case "/":
                _token = self.new_token(token.SLASH, self.char)
            case "*":
                _token = self.new_token(token.ASTERISK, self.char)
            case "<":
                _token = self.new_token(token.LT, self.char)
            case ">":
                _token = self.new_token(token.GT, self.char)
            case "{":
                _token = self.new_token(token.LBRACE, self.char)
            case "}":
                _token = self.new_token(token.RBRACE, self.char)
            case 0:
                _token = self.new_token(token.EOF, "")
            case _:
                if self.is_letter(self.char):
                    ident = self.read_identifier()
                    return self.new_token(token.lookup_identfier(ident), ident)
                elif self.is_digit(self.char):
                    return self.new_token(token.INT, self.read_number())
                _token = self.new_token(token.ILLEGAL, self.char)
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
