from dataclasses import dataclass
from typing import TypeAlias

TokenType: TypeAlias = str


@dataclass
class Token:
    type: TokenType
    literal: str


ILLEGAL = "ILLEGAL"
EOF = "EOF"

# Identifiers + literals
IDENT = "IDENT"  # add, foobar, x, y, ...
INT = "INT"  # 123456789

# Operators
ASSIGN = "="
PLUS = "+"

# Delimiters
COMMA = ","
SEMICOLON = ";"
LPAREN = "("
RPAREN = ")"
LBRACE = "{"
RBRACE = "}"

# Keywords
FUNCTION = "FUNCTION"
LET = "LET"


def keywords(name: str) -> TokenType | None:
    _keywords = {"fn": FUNCTION, "let": LET}
    return _keywords.get(name, None)


def lookup_identfier(ident: str) -> TokenType:
    if (token_type := keywords(ident)) is not None:
        return token_type
    return IDENT
