from interpret_deez import lexer, parser


def get_errors(errors: list) -> str:
    monkey_face = r'''            __,__
   .--.  .-"     "-.  .--.
  / .. \/  .-. .-.  \/ .. \
 | |  '|  /   Y   \  |'  | |
 | \   \  \ 0 | 0 /  /   / |
  \ '- ,\.-"""""""-./, -' /
   ''-' /_   ^ ^   _\ '-''
       |  \._   _./  |
       \   \ '~' /   /
        '._ '-=-' _.'
           '-----'
    '''
    # number of spaces is 5, the same as the last char in monkey's char until end of triple quotes
    error_message = "Woops! We ran into some monkey business here!\n     parser errors:\n"

    errors_output = ""
    for error in errors:
        errors_output = f"{errors_output}\t{error}\n"

    errors_output = f"{monkey_face}{error_message}{errors_output}"
    return errors_output


def emulate_parser(input: str) -> tuple[str, str]:
    lex = lexer.Lexer(input)
    pars = parser.Parser(lex)
    program = pars.parse_program()
    program_string = f">> {input}"
    errors_output = ""

    if len(pars.errors) != 0:
        errors_output = get_errors(pars.get_errors())
        errors_output = f"{program_string}\n{errors_output}"

    program_string = f"{program_string}\n{program.to_string()}\n"
    return program_string, errors_output


if __name__ == "__main__":
    input_1 = "let  = 1 * 2 * 3 * 4 * 5;"  # wrong input on purpose
    input_2 = "x * y / 2 + 3 * 8 - 123"
    input_3 = "true == false"
    inputs = [input_1, input_2, input_3]

    print("\nHello! This is the Monkey programming language!")
    print("Feel free to type in commands\n")

    for i, input in enumerate(inputs):
        out, errors = emulate_parser(input)
        print(f"<--------------- Parsing input {i+1}: --------------->")
        if errors:
            print(errors)
        else:
            print(out)
