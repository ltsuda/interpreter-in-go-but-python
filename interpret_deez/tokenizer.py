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
MINUS = "-"
BANG = "!"
ASTERISK = "*"
SLASH = "/"

LT = "<"
GT = ">"
EQ = "=="
NOT_EQ = "!="

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
TRUE = "TRUE"
FALSE = "FALSE"
IF = "IF"
ELSE = "ELSE"
RETURN = "RETURN"


def keywords(name: str) -> TokenType | None:
    _keywords = {
        "fn": FUNCTION,
        "let": LET,
        "true": TRUE,
        "false": FALSE,
        "if": IF,
        "else": ELSE,
        "return": RETURN,
    }
    return _keywords.get(name.lower(), None)


def lookup_identfier(ident: str) -> TokenType:
    if (token_type := keywords(ident)) is not None:
        return token_type
    return IDENT
