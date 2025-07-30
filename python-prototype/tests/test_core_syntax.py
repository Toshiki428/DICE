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

def test_interpreter_if_statement(run_dice_code):
    code = """
    func main() {
        a = 10;
        if (a == 10) {
            print("a is 10");
        } else {
            print("a is not 10");
        }
    }
    """
    output = run_dice_code(code)
    assert "a is 10" in output

def test_interpreter_if_else_statement(run_dice_code):
    code = """
    func main() {
        a = 20;
        if (a == 10) {
            print("a is 10");
        } else {
            print("a is not 10");
        }
    }
    """
    output = run_dice_code(code)
    assert "a is not 10" in output

def test_interpreter_comparison_operators(run_dice_code):
    # Equal
    assert "True" in run_dice_code('func main() { print(10 == 10); }')
    assert "False" in run_dice_code('func main() { print(10 == 5); }')

    # Not Equal
    assert "True" in run_dice_code('func main() { print(10 != 5); }')
    assert "False" in run_dice_code('func main() { print(10 != 10); }')

    # Less Than
    assert "True" in run_dice_code('func main() { print(5 < 10); }')
    assert "False" in run_dice_code('func main() { print(10 < 5); }')

    # Greater Than
    assert "True" in run_dice_code('func main() { print(10 > 5); }')
    assert "False" in run_dice_code('func main() { print(5 > 10); }')

    # Less Than or Equal
    assert "True" in run_dice_code('func main() { print(5 <= 5); }')
    assert "True" in run_dice_code('func main() { print(4 <= 5); }')
    assert "False" in run_dice_code('func main() { print(6 <= 5); }')

    # Greater Than or Equal
    assert "True" in run_dice_code('func main() { print(10 >= 10); }')
    assert "True" in run_dice_code('func main() { print(11 >= 10); }')
    assert "False" in run_dice_code('func main() { print(9 >= 10); }')

# --- Loop and Parallel Control Flow Tests ---

def test_interpreter_sequential_loop(run_dice_code):
    code = """
    func main() {
        loop i in 0..3 {
            print(i);
        }
    }
    """
    output = run_dice_code(code)
    output_lines = output.strip().split('\n')
    assert output_lines == ["0", "1", "2"]

def test_interpreter_parallel_loop(run_dice_code):
    code = """
    func main() {
        p loop i in 0..3 {
            wait(0.01 * (2-i)); // 意図的に逆順で終わるように待機
            print(i);
        }
    }
    """
    output = run_dice_code(code)
    output_lines = set(output.strip().split('\n'))
    assert output_lines == {"0", "1", "2"}

def test_interpreter_nested_parallelism_with_sequential_loop(run_dice_code):
    code = """
    func main() {
        p {
            // このループは p ブロックの直接の子ではないため、順次実行される
            loop i in 0..2 {
                print(i);
            }
            // 同時に実行されるタスク
            print("side task");
        }
    }
    """
    output = run_dice_code(code)
    output_lines = output.strip().split('\n')
    assert "0" in output_lines
    assert "1" in output_lines
    assert "side task" in output_lines
    assert output_lines.index("0") < output_lines.index("1")

def test_interpreter_sequential_inclusive_loop(run_dice_code):
    code = """
    func main() {
        loop i in 0..=3 {
            print(i);
        }
    }
    """
    output = run_dice_code(code)
    output_lines = output.strip().split('\n')
    assert output_lines == ["0", "1", "2", "3"]