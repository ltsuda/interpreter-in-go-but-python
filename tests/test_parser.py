from interpret_deez import ast, lexer, parser


def test_let_statement():
    input = """
    let x = 5;
    let y = 10;
    let foobar = 838383;
    """

    lex = lexer.Lexer(input)
    pars = parser.Parser(lex)
    program = pars.parse_program()

    assert isinstance(program, ast.Program), "parse_program() returned not ast.Program"
    assert (
        len(program.statements) == 3
    ), f"program.statements does not contain 3 statements. got={len(program.statements)}"

    expected = ["x", "y", "foobar"]

    for i, tt in enumerate(expected):
        print(f"{i=}, {tt=}")
        statement = program.statements[i]
        has_passed, error_message = check_let_statement(statement, tt)
        assert has_passed, error_message


def check_let_statement(statement: ast.Statement | ast.LetStatement, name: str) -> tuple[bool, str]:
    if statement.token_literal() != "let":
        return False, f"statement.token_literal() not 'let'. got={statement.token_literal()}"

    let_statement = ast.LetStatement(statement.token, statement.name, statement.value)
    if not isinstance(let_statement, ast.LetStatement):
        return False, f"statement not 'ast.LetStatement'. got={type(let_statement)}"

    if let_statement.name.value != name:
        return False, f"let_statement.name.value not '{name}'. got={let_statement.name.value}"

    if let_statement.name.token_literal() != name:
        return (
            False,
            f"let_statement.name.token_literal() not '{name}'."
            f"got={let_statement.name.token_literal()}",
        )

    return True, ""
