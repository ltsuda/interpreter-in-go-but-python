from dataclasses import dataclass
from typing import TypeAlias

TokenType: TypeAlias = str


@dataclass(frozen=True)
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
