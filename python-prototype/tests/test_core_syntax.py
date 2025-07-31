import pytest
import re
from parser import Parser
from tokenizer import Tokenizer

# --- Parser Error Tests ---

@pytest.mark.parametrize("code, error_message", [
    ("func main() { x = p {} }", "Cannot assign a ParallelNode to a variable."),
    ("func main() { x = if (true) {} }", "Cannot assign a IfNode to a variable."),
    ("func main() { x = loop i in 0..1 {} }", "Cannot assign a LoopNode to a variable."),
    ("func main() { 1 + }", "Unexpected token Token(type='RBRACE', value='}', line=1, column=19) at line 1"),
])
def test_parser_errors(code, error_message):
    """Ensures the parser raises SyntaxError for grammatically incorrect code."""
    with pytest.raises(SyntaxError, match=re.escape(error_message)):
        tokens = Tokenizer(code).tokenize()
        Parser(tokens).parse()

# --- Interpreter Tests ---

@pytest.mark.parametrize("code, expected_output", [
    ("print(10 + 2 * 3);", "16.0"),
    ("print((10 + 2) * 3);", "36.0"),
    ("print(10 / 2 - 1);", "4.0"),
])
def test_arithmetic_operations(run_dice_code, code, expected_output):
    """Tests basic arithmetic operations and operator precedence."""
    dice_code = f"func main() {{ {code} }}"
    assert expected_output in run_dice_code(dice_code)

@pytest.mark.parametrize("expression, expected_output", [
    # Equal
    ("10 == 10", "True"),
    ("10 == 5", "False"),
    # Not Equal
    ("10 != 5", "True"),
    ("10 != 10", "False"),
    # Less Than
    ("5 < 10", "True"),
    ("10 < 5", "False"),
    ("5 < 5", "False"),
    # Greater Than
    ("10 > 5", "True"),
    ("5 > 10", "False"),
    ("5 > 5", "False"),
    # Less Than or Equal
    ("5 <= 10", "True"),
    ("5 <= 5", "True"),
    ("10 <= 5", "False"),
    # Greater Than or Equal
    ("10 >= 5", "True"),
    ("10 >= 10", "True"),
    ("5 >= 10", "False"),
])
def test_comparison_operators(run_dice_code, expression, expected_output):
    """Tests all comparison operators for both true and false outcomes."""
    dice_code = f"func main() {{ print({expression}); }}"
    assert expected_output in run_dice_code(dice_code)

def test_variable_assignment_and_scope(run_dice_code):
    """Tests that variables are correctly assigned and scoped."""
    code = '''
    x = 10; // Global scope
    func my_func() {
        x = 20; // Local scope
        print("Inner x:", x);
    }
    func main() {
        my_func();
        print("Outer x:", x);
    }
    '''
    output = run_dice_code(code)
    assert "Inner x: 20.0" in output
    assert "Outer x: 10.0" in output

@pytest.mark.parametrize("return_val, expected_val", [
    ("123", "123.0"),
    ('"hello"', "hello"),
    ("true", "True"),
])
def test_return_statement(run_dice_code, return_val, expected_val):
    """Tests that `return` statements correctly return values of different types."""
    code = f'''
    func get_value() {{
        return {return_val};
    }}
    func main() {{
        result = get_value();
        print(result);
    }}
    '''
    assert expected_val in run_dice_code(code)

def test_function_without_return(run_dice_code):
    """Tests that a function without a return statement implicitly returns None."""
    code = '''
    func no_return() {
        a = 1;
    }
    func main() {
        result = no_return();
        print(result);
    }
    '''
    assert "None" in run_dice_code(code)

# --- Interpreter Runtime Error Tests ---

@pytest.mark.parametrize("code, error_type, match_message", [
    ("print(1 / 0);", ZeroDivisionError, "Division by zero"),
    ("print(undefined_var);", NameError, "'undefined_var' is not defined"),
])
def test_interpreter_runtime_errors(run_dice_code, code, error_type, match_message):
    """Ensures the interpreter raises appropriate errors for runtime exceptions."""
    dice_code = f"func main() {{ {code} }}"
    with pytest.raises(error_type, match=match_message):
        run_dice_code(dice_code)