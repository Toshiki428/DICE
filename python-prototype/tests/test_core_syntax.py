import pytest

from tokenizer import Tokenizer, Token
from parser import Parser
from interpreter import Interpreter

# --- Tokenizer Tests ---
def test_tokenizer_basic_tokens():
    code = "func main() { var = 10 + \"hello\"; }"
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()
    assert tokens[0].type == 'FUNC'
    assert tokens[1].type == 'IDENTIFIER'
    assert tokens[1].value == 'main'
    assert tokens[5].type == 'IDENTIFIER'
    assert tokens[5].value == 'var'
    assert tokens[7].type == 'NUMBER'
    assert tokens[7].value == '10'
    assert tokens[8].type == 'PLUS'
    assert tokens[9].type == 'STRING'
    assert tokens[9].value == '"hello"'

# --- Parser Tests ---
def test_parser_func_def():
    code = "func my_func() { wait(1); }"
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    assert ast is not None
    assert len(ast.statements) == 1
    assert ast.statements[0].__class__.__name__ == 'FuncDefNode'
    assert ast.statements[0].name == 'my_func'

def test_parser_assignment_and_arithmetic():
    code = "func main() { a = 1 + 2 * 3; }"
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    assert ast is not None

# --- Interpreter Tests ---
def test_interpreter_arithmetic(run_dice_code):
    code = "func main() { print(10 + 5 - 2 * 3 / 2); }"
    output = run_dice_code(code)
    # 10 + 5 - 3 = 12
    assert "12.0" in output

def test_interpreter_variable_assignment(run_dice_code):
    code = "func main() { x = 10; print(x); }"
    output = run_dice_code(code)
    assert "10.0" in output

def test_interpreter_function_call(run_dice_code):
    code = """
    func greet(name) {
        print("Hello, " + name);
    }
    func main() {
        greet("World");
    }
    """
    output = run_dice_code(code)
    assert "Hello, World" in output

def test_interpreter_boolean_values(run_dice_code):
    code = """
    func main() {
        a = true;
        b = false;
        print(a);
        print(b);
    }
    """
    output = run_dice_code(code)
    assert "True" in output
    assert "False" in output