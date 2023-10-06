# type: ignore[reportOptionalMemberAccess, reportGeneralTypeIssues]

import pytest
from pytest_check import check

from interpret_deez import ast, lexer, parser


@pytest.mark.parametrize(
    "input, expected_ident, expected_value",
    [
        ("let x = 5;", "x", 5),
        ("let y = True;", "y", True),
        ("let foobar = y;", "foobar", "y"),
    ],
)
def test_let_statements(input, expected_ident, expected_value):
    lex = lexer.Lexer(input)
    pars = parser.Parser(lex)
    program = pars.parse_program()
    statements = program.statements

    assert (
        len(statements) == 1
    ), f"program.statements does not contain 1 statement. got={len(statements)}"

    statement: ast.LetStatement = program.statements[0]
    has_passed, error_message = check_let_statement(statement, expected_ident)
    assert has_passed, error_message

    value = statement.value
    has_passed, error_message = check_literal_expression(value, expected_value)
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
    "input,expected_value",
    [
        ("return 5;", 5),
        ("return True;", True),
        ("return foobar;", "foobar"),
    ],
)
def test_return_statements(input, expected_value):
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
    has_passed, error_message = check_literal_expression(statement.return_value, expected_value)
    assert has_passed, error_message


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


def test_function_literal_expression():
    input = "fn(x, y) { x + y; }"

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
    ), f"program.statement[0] is not ast.ExpressionStatement. got={type(statement)}"

    fn_expression = statement.expression
    assert isinstance(
        fn_expression, ast.FunctionLiteral
    ), f"fn_expression is not ast.FunctionLiteral. got={type(fn_expression)}"

    assert (
        len(fn_expression.parameters) == 2
    ), f"function literal parameters are wrong. want 2, got={len(fn_expression.parameters)}"

    passed, message = check_literal_expression(fn_expression.parameters[0], "x")
    assert passed, message
    passed, message = check_literal_expression(fn_expression.parameters[1], "y")
    assert passed, message

    assert len(fn_expression.body.statements) == 1, (
        f"fn_expression.body.statements has not 1 statements, "
        f"got={len(fn_expression.body.statements)}"
    )
    body_statement = fn_expression.body.statements[0]
    assert isinstance(
        body_statement, ast.ExpressionStatement
    ), f"function body statement is not ast.ExpressionStatement. got={type(body_statement)}"
    passed, message = check_infix_expression(body_statement.expression, "x", "+", "y")
    assert passed, message


@pytest.mark.parametrize(
    "input,expected_params",
    [
        (r"fn() {};", []),
        (r"fn(x) {}", ["x"]),
        (r"fn(x, y, z) {}", ["x", "y", "z"]),
    ],
)
def test_function_parameters_expression(input, expected_params):
    lex = lexer.Lexer(input)
    pars = parser.Parser(lex)
    program = pars.parse_program()
    check_parse_errors(pars)

    statement: ast.ExpressionStatement = program.statements[0]
    fn: ast.FunctionLiteral = statement.expression

    assert len(fn.parameters) == len(
        expected_params
    ), f"length parameters wrong. want {len(expected_params)}, got={len(fn.parameters)}"

    for i, ident in enumerate(expected_params):
        passed, message = check_literal_expression(fn.parameters[i], ident)
        assert passed, message


def test_call_expression():
    input = "add(1, 2 * 3, 4 + 5);"

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
    ), f"program.statement[0] is not ast.ExpressionStatement. got={type(statement)}"

    expression: ast.CallExpression = statement.expression
    assert isinstance(
        expression, ast.CallExpression
    ), f"expression is not ast.CallExpression. got={type(expression)}"

    passed, message = check_identifier(expression.function, "add")
    assert passed, message

    assert (
        len(expression.arguments) == 3
    ), f"wrong length of arguments. got={len(expression.arguments)}"

    passed, message = check_literal_expression(expression.arguments[0], 1)
    assert passed, message
    passed, message = check_infix_expression(expression.arguments[1], 2, "*", 3)
    assert passed, message
    passed, message = check_infix_expression(expression.arguments[2], 4, "+", 5)
    assert passed, message


@pytest.mark.parametrize(
    "input,expected",
    [
        ("False;", False),
        ("True;", True),
    ],
)
def test_boolean_expression(input, expected):
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

    passed, message = check_literal_expression(statement.expression, expected)
    assert passed, message


@pytest.mark.parametrize(
    "input,operator,int_value",
    [
        ("!5;", "!", 5),
        ("-15;", "-", 15),
        ("!True;", "!", True),
        ("!False;", "!", False),
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
        ("True == True;", True, "==", True),
        ("True != False;", True, "!=", False),
        ("False == False;", False, "==", False),
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
        ("True", "True"),
        ("False", "False"),
        ("3 > 5 == False", "((3 > 5) == False)"),
        ("3 < 5 == True", "((3 < 5) == True)"),
        ("1 + (2 + 3) + 4", "((1 + (2 + 3)) + 4)"),
        ("(5 + 5) * 2", "((5 + 5) * 2)"),
        ("2 / (5 + 5)", "(2 / (5 + 5))"),
        ("-(5 + 5)", "(-(5 + 5))"),
        ("!(True == True)", "(!(True == True))"),
        ("a + add(b * c) + d", "((a + add((b * c))) + d)"),
        (
            "add(a, b, 1, 2 * 3, 4 + 5, add(6, 7 * 8))",
            "add(a, b, 1, (2 * 3), (4 + 5), add(6, (7 * 8)))",
        ),
        ("add(a + b + c * d / e + f)", "add((((a + b) + ((c * d) / e)) + f))"),
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


def test_if_expression():
    input = "if (x < y) { x };"

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

    expression = statement.expression
    assert isinstance(
        expression, ast.IfExpression
    ), f"expression is not ast.IfExpression. got={type(expression)}"

    passed, message = check_infix_expression(expression.condition, "x", "<", "y")
    assert passed, message

    assert (
        len(expression.consequence.statements) == 1
    ), f"consequence is not 1 statement. got={len(expression.consequence.statements)}"

    consequence = expression.consequence.statements[0]
    assert isinstance(
        consequence, ast.ExpressionStatement
    ), f"consequence is not ast.ExpressionStatement. got={type(consequence)}"

    passed, message = check_identifier(consequence.expression, "x")
    assert passed, message

    assert (
        expression.alternative is None
    ), f"expression.alternative.statements was not None. got={expression.alternative}"


def test_if_else_expression():
    input = "if (x < y) { x } else { y };"

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

    expression = statement.expression
    assert isinstance(
        expression, ast.IfExpression
    ), f"expression is not ast.IfExpression. got={type(expression)}"

    passed, message = check_infix_expression(expression.condition, "x", "<", "y")
    assert passed, message

    assert (
        len(expression.consequence.statements) == 1
    ), f"concequence is not 1 statement. got={len(expression.consequence.statements)}"

    consequence = expression.consequence.statements[0]
    assert isinstance(
        consequence, ast.ExpressionStatement
    ), f"consequence is not ast.ExpressionStatement. got={type(consequence)}"

    passed, message = check_identifier(consequence.expression, "x")
    assert passed, message

    assert len(expression.alternative.statements) == 1, (
        f"expression.alternative.statements does not contain 1 statement. "
        f"got={len(expression.alternative.statements)}"
    )

    alternative = expression.alternative.statements[0]
    assert isinstance(
        alternative, ast.ExpressionStatement
    ), f"alternative is not ast.ExpressionStatement. got={type(alternative)}"

    passed, message = check_identifier(alternative.expression, "y")
    assert passed, message


def check_let_statement(statement: ast.Statement, name: str) -> tuple[bool, str]:
    if statement.token_literal() != "let":
        return False, f"statement.token_literal() not 'let'. got={statement.token_literal()}"

    if not isinstance(statement, ast.LetStatement):
        return False, f"statement not 'ast.LetStatement'. got={type(statement)}"

    if statement.name.value != name:
        return (
            False,
            f"statement.name.value not '{name}'." f"got={statement.name.value}",
        )
    if statement.name.token_literal() != name:
        return (
            False,
            f"statement.name.token_literal() not '{name}'." f"got={statement.name.token_literal()}",
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
            check.equal("parser has 0 errors", error_title)
        check.equal("no parser error", error)


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
        return False, f"identifier.token_literal() not {expected}. got={expression.token_literal()}"

    return True, ""


def check_boolean(expression: ast.Expression | None, expected: bool) -> tuple[bool, str]:
    if not isinstance(expression, ast.Boolean):
        return False, f"expression not ast.Boolean. got={expression}"

    if expression.value is not expected:
        return False, f"boolean.value not {expected}. got={expression.value}"

    if expression.token_literal() != str(expected):
        return False, f"boolean.token_literal() not {expected}. got={expression.token_literal()}"

    return True, ""


def check_literal_expression(
    expression: ast.Expression | None, expected: int | str | bool
) -> tuple[bool, str]:
    match expected:
        case bool():  # This must be first for bool parse to work. Need to know why.
            return check_boolean(expression, expected)
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
