import pytest
from io import StringIO

from tokenizer import Tokenizer
from parser import Parser
from interpreter import Interpreter

@pytest.fixture
def run_dice_code(capsys):
    """
    A pytest fixture that provides a function to execute DICE code.

    This fixture encapsulates the entire process of tokenizing, parsing,
    and interpreting a given string of DICE code. It captures and returns
    the standard output, allowing tests to assert against what the code prints.

    Args:
        capsys: The pytest fixture for capturing stdout and stderr.

    Returns:
        A function that takes a string of DICE code and returns its stdout.
    """
    def _run_dice_code(code):
        tokenizer = Tokenizer(code)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        interpreter = Interpreter()
        interpreter.interpret(ast)
        captured = capsys.readouterr()
        return captured.out
    return _run_dice_code
