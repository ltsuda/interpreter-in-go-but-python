from interpret_deez import ast, tokenizer
from interpret_deez.ast import Identifier, LetStatement


def test_ast_to_string():
    """Test 'let myVar = anotherVar;' AST to string"""
    let_statement = LetStatement(
        token=tokenizer.Token(tokenizer.LET, "let"),
        name=Identifier(tokenizer.Token(tokenizer.IDENT, "myVar"), "myVar"),
        value=Identifier(tokenizer.Token(tokenizer.IDENT, "anotherVar"), "anotherVar"),
    )

    program = ast.Program([let_statement])

    assert (
        program.to_string() == "let myVar = anotherVar;"
    ), f"program.to_string() wrong. got={program.to_string()}"
