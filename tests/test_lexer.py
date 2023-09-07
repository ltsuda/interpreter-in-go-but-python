from interpret_deez import tokenizer
from interpret_deez.lexer import Lexer


def test_next_token():
    input = """
        let five = 5;
        let ten = 10;
        let add = fn(x, y) {
            x + y;
        };

        let result = add(five, ten);
        !-/*5[];
        5 < 10 > 5;

        if (5 < 10) {
            return true;
        } else {
            return false;
        }

        10 == 10;
        10 != 9;
    """

    expected: list[tokenizer.Token] = [
        tokenizer.Token(tokenizer.LET, "let"),
        tokenizer.Token(tokenizer.IDENT, "five"),
        tokenizer.Token(tokenizer.ASSIGN, "="),
        tokenizer.Token(tokenizer.INT, "5"),
        tokenizer.Token(tokenizer.SEMICOLON, ";"),
        tokenizer.Token(tokenizer.LET, "let"),
        tokenizer.Token(tokenizer.IDENT, "ten"),
        tokenizer.Token(tokenizer.ASSIGN, "="),
        tokenizer.Token(tokenizer.INT, "10"),
        tokenizer.Token(tokenizer.SEMICOLON, ";"),
        tokenizer.Token(tokenizer.LET, "let"),
        tokenizer.Token(tokenizer.IDENT, "add"),
        tokenizer.Token(tokenizer.ASSIGN, "="),
        tokenizer.Token(tokenizer.FUNCTION, "fn"),
        tokenizer.Token(tokenizer.LPAREN, "("),
        tokenizer.Token(tokenizer.IDENT, "x"),
        tokenizer.Token(tokenizer.COMMA, ","),
        tokenizer.Token(tokenizer.IDENT, "y"),
        tokenizer.Token(tokenizer.RPAREN, ")"),
        tokenizer.Token(tokenizer.LBRACE, "{"),
        tokenizer.Token(tokenizer.IDENT, "x"),
        tokenizer.Token(tokenizer.PLUS, "+"),
        tokenizer.Token(tokenizer.IDENT, "y"),
        tokenizer.Token(tokenizer.SEMICOLON, ";"),
        tokenizer.Token(tokenizer.RBRACE, "}"),
        tokenizer.Token(tokenizer.SEMICOLON, ";"),
        tokenizer.Token(tokenizer.LET, "let"),
        tokenizer.Token(tokenizer.IDENT, "result"),
        tokenizer.Token(tokenizer.ASSIGN, "="),
        tokenizer.Token(tokenizer.IDENT, "add"),
        tokenizer.Token(tokenizer.LPAREN, "("),
        tokenizer.Token(tokenizer.IDENT, "five"),
        tokenizer.Token(tokenizer.COMMA, ","),
        tokenizer.Token(tokenizer.IDENT, "ten"),
        tokenizer.Token(tokenizer.RPAREN, ")"),
        tokenizer.Token(tokenizer.SEMICOLON, ";"),
        tokenizer.Token(tokenizer.BANG, "!"),
        tokenizer.Token(tokenizer.MINUS, "-"),
        tokenizer.Token(tokenizer.SLASH, "/"),
        tokenizer.Token(tokenizer.ASTERISK, "*"),
        tokenizer.Token(tokenizer.INT, "5"),
        tokenizer.Token(tokenizer.LBRACKET, "["),
        tokenizer.Token(tokenizer.RBRACKET, "]"),
        tokenizer.Token(tokenizer.SEMICOLON, ";"),
        tokenizer.Token(tokenizer.INT, "5"),
        tokenizer.Token(tokenizer.LT, "<"),
        tokenizer.Token(tokenizer.INT, "10"),
        tokenizer.Token(tokenizer.GT, ">"),
        tokenizer.Token(tokenizer.INT, "5"),
        tokenizer.Token(tokenizer.SEMICOLON, ";"),
        tokenizer.Token(tokenizer.IF, "if"),
        tokenizer.Token(tokenizer.LPAREN, "("),
        tokenizer.Token(tokenizer.INT, "5"),
        tokenizer.Token(tokenizer.LT, "<"),
        tokenizer.Token(tokenizer.INT, "10"),
        tokenizer.Token(tokenizer.RPAREN, ")"),
        tokenizer.Token(tokenizer.LBRACE, "{"),
        tokenizer.Token(tokenizer.RETURN, "return"),
        tokenizer.Token(tokenizer.TRUE, "true"),
        tokenizer.Token(tokenizer.SEMICOLON, ";"),
        tokenizer.Token(tokenizer.RBRACE, "}"),
        tokenizer.Token(tokenizer.ELSE, "else"),
        tokenizer.Token(tokenizer.LBRACE, "{"),
        tokenizer.Token(tokenizer.RETURN, "return"),
        tokenizer.Token(tokenizer.FALSE, "false"),
        tokenizer.Token(tokenizer.SEMICOLON, ";"),
        tokenizer.Token(tokenizer.RBRACE, "}"),
        tokenizer.Token(tokenizer.INT, "10"),
        tokenizer.Token(tokenizer.EQ, "=="),
        tokenizer.Token(tokenizer.INT, "10"),
        tokenizer.Token(tokenizer.SEMICOLON, ";"),
        tokenizer.Token(tokenizer.INT, "10"),
        tokenizer.Token(tokenizer.NOT_EQ, "!="),
        tokenizer.Token(tokenizer.INT, "9"),
        tokenizer.Token(tokenizer.SEMICOLON, ";"),
        tokenizer.Token(tokenizer.EOF, ""),
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
