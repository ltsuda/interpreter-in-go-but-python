import pytest
from pytest_check import check

from interpret_deez import ast, lexer, parser


@pytest.mark.parametrize(
    "input, expected",
    [
        ("let x = 5;", "x"),
        ("let y = 10;", "y"),
        ("let foobar = 838383;", "foobar"),
    ],
)
def test_let_statement(input, expected):
    lex = lexer.Lexer(input)
    pars = parser.Parser(lex)
    program = pars.parse_program()
    statements = program.statements

    assert isinstance(program, ast.Program), "parse_program() returned not ast.Program"
    assert (
        len(statements) == 1
    ), f"program.statements does not contain 1 statement. got={len(statements)}"

    statement = program.statements[0]
    has_passed, error_message = check_let_statement(statement, expected)
    assert has_passed, error_message


@pytest.mark.skip("should fail after all parsers are implemented")
@pytest.mark.parametrize(
    "input",
    [
        ("let z 123456;"),
        ("let = 11;"),
        ("let 654321;"),
    ],
)
def test_parse_errors_should_fail(input):
    """Test should fail on purpose to show parse errors"""
    lex = lexer.Lexer(input)
    pars = parser.Parser(lex)
    pars.parse_program()
    check_parse_errors(pars)


@pytest.mark.parametrize(
    "input",
    [
        ("return 5;"),
        ("return 10;"),
        ("return 123123;"),
    ],
)
def test_return_statements(input):
    lex = lexer.Lexer(input)
    pars = parser.Parser(lex)
    program = pars.parse_program()
    check_parse_errors(pars)

    assert (
        len(program.statements) == 1
    ), f"program.statements does not contain 1 statements. got={len(program.statements)}"

    statement = program.statements[0]
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

    passed, message = check_literal_expression(statement.expression, "foobar")
    assert passed, message


def test_integer_literal_expression():
    input = "100;"

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

    passed, message = check_literal_expression(statement.expression, 100)
    assert passed, message


@pytest.mark.parametrize(
    "input,operator,int_value",
    [
        ("!5;", "!", 5),
        ("-15;", "-", 15),
    ],
)
def test_prefix_expressions(input, operator, int_value):
    lex = lexer.Lexer(input)
    pars = parser.Parser(lex)
    program = pars.parse_program()
    check_parse_errors(pars)

    assert (
        len(program.statements) == 1
    ), f"program.statements does not contain 1 statements. got={len(program.statements)}"

    statement = program.statements[0]
    assert isinstance(
        statement, ast.ExpressionStatement
    ), f"program.statement[0] is not ast.ExpressionStatement. got={statement}"

    prefix_expression = statement.expression
    assert isinstance(
        prefix_expression, ast.PrefixExpression
    ), f"expression not ast.PrefixExpression. got={prefix_expression}"

    assert (
        prefix_expression.operator == operator
    ), f"prefix_expression.operator is not {operator}. got={prefix_expression.operator}"

    passed, message = check_literal_expression(prefix_expression.right, int_value)
    assert passed, message


@pytest.mark.parametrize(
    "input,left,operator,right",
    [
        ("5 + 5;", 5, "+", 5),
        ("5 - 5;", 5, "-", 5),
        ("5 * 5;", 5, "*", 5),
        ("5 / 5;", 5, "/", 5),
        ("5 > 5;", 5, ">", 5),
        ("5 < 5;", 5, "<", 5),
        ("5 == 5;", 5, "==", 5),
        ("5 != 5;", 5, "!=", 5),
    ],
)
def test_infix_expressions(input, left, operator, right):
    lex = lexer.Lexer(input)
    pars = parser.Parser(lex)
    program = pars.parse_program()
    check_parse_errors(pars)

    assert (
        len(program.statements) == 1
    ), f"program.statements does not contain 1 statements. got={len(program.statements)}"

    statement = program.statements[0]
    assert isinstance(
        statement, ast.ExpressionStatement
    ), f"program.statement[0] is not ast.ExpressionStatement. got={type(statement)}"

    infix_expression = statement.expression
    passed, message = check_infix_expression(infix_expression, left, operator, right)
    assert passed, message


@pytest.mark.parametrize(
    "input,expected",
    [
        ("-a * b", "((-a) * b)"),
        ("!-a", "(!(-a))"),
        ("a + b + c", "((a + b) + c)"),
        ("a + b - c", "((a + b) - c)"),
        ("a * b * c", "((a * b) * c)"),
        ("a * b / c", "((a * b) / c)"),
        ("a + b / c", "(a + (b / c))"),
        ("a + b * c + d / e - f", "(((a + (b * c)) + (d / e)) - f)"),
        ("3 + 4; -5 * 5", "(3 + 4)((-5) * 5)"),
        ("5 > 4 == 3 < 4", "((5 > 4) == (3 < 4))"),
        ("5 < 4 != 3 > 4", "((5 < 4) != (3 > 4))"),
        ("3 + 4 * 5 == 3 * 1 + 4 * 5", "((3 + (4 * 5)) == ((3 * 1) + (4 * 5)))"),
    ],
)
def test_operator_precedence(input, expected):
    lex = lexer.Lexer(input)
    pars = parser.Parser(lex)
    program = pars.parse_program()
    check_parse_errors(pars)

    program_string = program.to_string()
    assert program_string == expected, f"expected={expected}, got={program_string}"


@pytest.mark.parametrize(
    "input,expected",
    [
        ("-1 * 2 + 3", "(((-1) * 2) + 3)"),
    ],
)
def test_tracer_operator_precedence(input, expected):
    lex = lexer.Lexer(input)
    pars = parser.Parser(lex, enable_defer=True)
    program = pars.parse_program()
    check_parse_errors(pars)

    program_string = program.to_string()
    assert program_string == expected, f"expected={expected}, got={program_string}"


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


def check_integer_literal(int_literal: ast.Expression | None, expected: int) -> tuple[bool, str]:
    if not isinstance(int_literal, ast.IntegerLiteral):
        return False, f"int_literal not ast.IntegerLiteral. got={type(int_literal)}"

    if int_literal.value != expected:
        return False, f"int_literal.value not {expected}. got={int_literal.value}"

    if int_literal.token_literal() != str(expected):
        return (
            False,
            f"int_literal.token_literal() not {expected}. got={int_literal.token_literal()}",
        )

    return True, ""


def check_identifier(expression: ast.Expression | None, expected: str) -> tuple[bool, str]:
    if not isinstance(expression, ast.Identifier):
        return False, f"expression not ast.Identifier. got={expression}"

    if expression.value != expected:
        return False, f"identifier.value not {expected}. got={expression.value}"

    if expression.token_literal() != expected:
        return False, f"identifier.token_literaL() not {expected}. got={expression.token_literal()}"

    return True, ""


def check_literal_expression(
    expression: ast.Expression | None, expected: int | str
) -> tuple[bool, str]:
    match expected:
        case int():
            return check_integer_literal(expression, int(expected))
        case str():
            return check_identifier(expression, str(expected))
        case _:
            return False, f"type of expected not handled. got={expected}"


def check_infix_expression(
    expression: ast.Expression | None, left, operator: str, right
) -> tuple[bool, str]:
    if not isinstance(expression, ast.InfixExpression):
        return False, f"expression is not ast.InfixExpression. got={type(expression)}({expression})"

    passed, message = check_literal_expression(expression.left, left)
    if not passed:
        return False, message

    if expression.operator != operator:
        return False, f"expression.operator is not {operator}. got={expression.operator}"

    passed, message = check_literal_expression(expression.right, right)
    if not passed:
        return False, message

    return True, ""
