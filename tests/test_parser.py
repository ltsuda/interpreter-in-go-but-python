import pytest
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


@pytest.mark.skip("should fail after all parsers are implemented")
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

    literal = statement.expression
    assert isinstance(
        literal, ast.IntegerLiteral
    ), f"expression not ast.IntegerLiteral. got={literal}"

    assert literal.value == 100, f"literal.value not 100. got={literal.value}"
    assert (
        literal.token_literal() == "100"
    ), f"literal.token_literaL() not '100'. got={literal.token_literal()}"


def test_prefix_expressions():
    tests = [
        {"input": "!5;", "operator": "!", "int_value": 5},
        {"input": "-15;", "operator": "-", "int_value": 15},
    ]

    for _, test in enumerate(tests):
        lex = lexer.Lexer(test["input"])
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
            prefix_expression.operator == test["operator"]
        ), f"prefix_expression.operator is not {test['operator']}. got={prefix_expression.operator}"

        passed, message = check_integer_literal(prefix_expression.right, test["int_value"])
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
    assert isinstance(
        infix_expression, ast.InfixExpression
    ), f"expression not ast.InfixExpression. got={type(infix_expression)}"

    passed, message = check_integer_literal(infix_expression.left, left)
    assert passed, message

    assert (
        infix_expression.operator == operator
    ), f"infix_expression.operator is not {operator}. got={infix_expression.operator}"

    passed, message = check_integer_literal(infix_expression.right, right)
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


def check_integer_literal(int_literal: ast.Expression | None, value: int) -> tuple[bool, str]:
    if not isinstance(int_literal, ast.IntegerLiteral):
        return False, f"int_literal not ast.IntegerLiteral. got={type(int_literal)}"

    if int_literal.value != value:
        return False, f"int_literal.value not {value}. got={int_literal.value}"

    if int_literal.token_literal() != str(value):
        return False, f"int_literal.token_literal() not {value}. got={int_literal.token_literal()}"

    return True, ""
