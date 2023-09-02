from interpret_deez import token
from interpret_deez.lexer import Lexer


def test_next_token():
    input = """
        let five = 5;
        let ten = 10;
        let add = fn(x, y) {
            x + y;
        };

        let result = add(five, ten);
        !-/*5;
        5 < 10 > 5;

        if (5 < 10) {
            return true;
        } else {
            return false;
        }

        10 == 10;
        10 != 9;
    """

    expected: list[token.Token] = [
        token.Token(token.LET, "let"),
        token.Token(token.IDENT, "five"),
        token.Token(token.ASSIGN, "="),
        token.Token(token.INT, "5"),
        token.Token(token.SEMICOLON, ";"),
        token.Token(token.LET, "let"),
        token.Token(token.IDENT, "ten"),
        token.Token(token.ASSIGN, "="),
        token.Token(token.INT, "10"),
        token.Token(token.SEMICOLON, ";"),
        token.Token(token.LET, "let"),
        token.Token(token.IDENT, "add"),
        token.Token(token.ASSIGN, "="),
        token.Token(token.FUNCTION, "fn"),
        token.Token(token.LPAREN, "("),
        token.Token(token.IDENT, "x"),
        token.Token(token.COMMA, ","),
        token.Token(token.IDENT, "y"),
        token.Token(token.RPAREN, ")"),
        token.Token(token.LBRACE, "{"),
        token.Token(token.IDENT, "x"),
        token.Token(token.PLUS, "+"),
        token.Token(token.IDENT, "y"),
        token.Token(token.SEMICOLON, ";"),
        token.Token(token.RBRACE, "}"),
        token.Token(token.SEMICOLON, ";"),
        token.Token(token.LET, "let"),
        token.Token(token.IDENT, "result"),
        token.Token(token.ASSIGN, "="),
        token.Token(token.IDENT, "add"),
        token.Token(token.LPAREN, "("),
        token.Token(token.IDENT, "five"),
        token.Token(token.COMMA, ","),
        token.Token(token.IDENT, "ten"),
        token.Token(token.RPAREN, ")"),
        token.Token(token.SEMICOLON, ";"),
        token.Token(token.BANG, "!"),
        token.Token(token.MINUS, "-"),
        token.Token(token.SLASH, "/"),
        token.Token(token.ASTERISK, "*"),
        token.Token(token.INT, "5"),
        token.Token(token.SEMICOLON, ";"),
        token.Token(token.INT, "5"),
        token.Token(token.LT, "<"),
        token.Token(token.INT, "10"),
        token.Token(token.GT, ">"),
        token.Token(token.INT, "5"),
        token.Token(token.SEMICOLON, ";"),
        token.Token(token.IF, "if"),
        token.Token(token.LPAREN, "("),
        token.Token(token.INT, "5"),
        token.Token(token.LT, "<"),
        token.Token(token.INT, "10"),
        token.Token(token.RPAREN, ")"),
        token.Token(token.LBRACE, "{"),
        token.Token(token.RETURN, "return"),
        token.Token(token.TRUE, "true"),
        token.Token(token.SEMICOLON, ";"),
        token.Token(token.RBRACE, "}"),
        token.Token(token.ELSE, "else"),
        token.Token(token.LBRACE, "{"),
        token.Token(token.RETURN, "return"),
        token.Token(token.FALSE, "false"),
        token.Token(token.SEMICOLON, ";"),
        token.Token(token.RBRACE, "}"),
        token.Token(token.INT, "10"),
        token.Token(token.EQ, "=="),
        token.Token(token.INT, "10"),
        token.Token(token.SEMICOLON, ";"),
        token.Token(token.INT, "10"),
        token.Token(token.NOT_EQ, "!="),
        token.Token(token.INT, "9"),
        token.Token(token.SEMICOLON, ";"),
        token.Token(token.EOF, ""),
    ]

    lexer = Lexer(input)

    for i, tt in enumerate(expected):
        next_token = lexer.next_token()

        assert (
            next_token.type == tt.type
        ), f"expected[{i}] - token type is wrong. expected: {tt.type}, got: {next_token.type}"

        assert (
            next_token.literal == tt.literal
        ), f"expected[{i}] - literal is wrong. expected: {tt.literal}, got: {next_token.literal}"
