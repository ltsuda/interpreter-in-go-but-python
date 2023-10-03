from interpret_deez import ast, lexer, parser
from pytest_check import check


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
        statement = program.statements[i]
        has_passed, error_message = check_let_statement(statement, tt)
        assert has_passed, error_message


def test_parse_errors_should_fail():
    """Test should fail on purpose to show parse errors"""

    input = """
    let z 123456;
    let = 11;
    let 654321;
    """

    lex = lexer.Lexer(input)
    pars = parser.Parser(lex)
    pars.parse_program()
    check_parse_errors(pars)


def test_return_statements():
    input = """
    return 5;
    return 10;
    return 123123;
    """

    lex = lexer.Lexer(input)
    pars = parser.Parser(lex)
    program = pars.parse_program()
    check_parse_errors(pars)

    assert (
        len(program.statements) == 3
    ), f"program.statements does not contain 3 statements. got={len(program.statements)}"

    for statement in program.statements:
        assert isinstance(
            statement, ast.ReturnStatement
        ), f"statement not 'ast.ReturnStatement'. got={type(statement)}"
        assert (
            statement.token_literal()
            != f"return_statement.token_literal() not 'return', got={statement.token_literal()}"
        )


def test_identifier_expression():
    input = "foobar;"

    lex = lexer.Lexer(input)
    pars = parser.Parser(lex)
    program = pars.parse_program()
    check_parse_errors(pars)

    assert (
        len(program.statements) == 1
    ), f"program.statements has not enough statements. got={len(program.statements)}"
    statement = program.statements[0]

    assert isinstance(
        statement, ast.ExpressionStatement
    ), f"program.statement[0] is not ast.ExpressionStatement. got={statement}"

    identifier = statement.expression
    assert isinstance(
        identifier, ast.Identifier
    ), f"expression not ast.Identifier. got={identifier}"

    assert identifier.value == "foobar", f"identifier.value not 'foobar'. got={identifier.value}"
    assert (
        identifier.token_literal() == "foobar"
    ), f"identifier.token_literaL() not 'foobar'. got={identifier.token_literal()}"


def check_let_statement(statement: ast.Statement, name: str) -> tuple[bool, str]:
    if statement.token_literal() != "let":
        return False, f"statement.token_literal() not 'let'. got={statement.token_literal()}"

    if not isinstance(statement, ast.LetStatement):
        return False, f"statement not 'ast.LetStatement'. got={type(statement)}"

    if statement.name.value != name:  # type: ignore[reportOptionalMemberAccess]
        return (
            False,
            f"statement.name.value not '{name}'."
            f"got={statement.name.value}",  # type: ignore[reportOptionalMemberAccess]
        )
    if statement.name.token_literal() != name:  # type: ignore[reportOptionalMemberAccess]
        return (
            False,
            f"statement.name.token_literal() not '{name}'."
            f"got={statement.name.token_literal()}",  # type: ignore[reportOptionalMemberAccess]
        )

    return True, ""


def check_parse_errors(pars: parser.Parser) -> None:
    errors = pars.get_errors()
    if not errors:
        return None

    error_title = f"parser has {len(errors)} errors"
    error_messages = []
    for _, message in enumerate(errors):
        error_messages.extend([f"parser error: {message}"])
    for i, error in enumerate(error_messages):
        if i == 0:
            check.equal("parser has 0 errors", error_title)  # type: ignore[reportGeneralTypeIssues]
        check.equal("no parser error", error)  # type: ignore[reportGeneralTypeIssues]
