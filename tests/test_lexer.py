from interpret_deez import token
from interpret_deez.lexer import Lexer


def test_next_token():
    input = "=+(){},;"

    expected: list[token.Token] = [
        token.Token(token.ASSIGN, "="),
        token.Token(token.PLUS, "+"),
        token.Token(token.LPAREN, "("),
        token.Token(token.RPAREN, ")"),
        token.Token(token.LBRACE, "{"),
        token.Token(token.RBRACE, "}"),
        token.Token(token.COMMA, ","),
        token.Token(token.SEMICOLON, ";"),
        token.Token(token.EOF, ""),
    ]

    lexer = Lexer(input)

    for i, tt in enumerate(expected):
        next_token = lexer.next_token()

        assert (
            next_token.type == tt.type
        ), f"expected[{i}] - token type is wrong. expected: {tt.type}, got: {next_token.literal}"

        assert (
            next_token.literal == tt.literal
        ), f"expected[{i}] - literal is wrong. expected: {tt.literal}, got: {next_token.literal}"
