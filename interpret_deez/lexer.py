from dataclasses import dataclass
from email.policy import default

from interpret_deez import token


@dataclass
class Lexer:
    inp: str
    position = 0
    read_position = 0
    char = 0

    def __post_init__(self):
        self.read_char()

    def read_char(self) -> None:
        print("from read_char")
        print(self.read_position)
        print(len(self.inp))
        if self.read_position >= len(self.inp):
            self.char = 0
        else:
            self.char = self.inp[self.read_position]
        self.position = self.read_position
        self.read_position += 1
        print(self.char)
        print(self.position)
        print(self.read_position)
        print("end read_char")

    def new_token(self, token_type: token.TokenType, char) -> token.Token:
        return token.Token(type=token_type, literal=str(char))

    def next_token(self) -> token.Token:
        _token: token.Token

        match self.char:
            case "=":
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
            case "{":
                _token = self.new_token(token.LBRACE, self.char)
            case "}":
                _token = self.new_token(token.RBRACE, self.char)
            case _:
                _token = self.new_token(token.EOF, "")
        print(f"from next_token: {_token}")
        self.read_char()
        return _token
