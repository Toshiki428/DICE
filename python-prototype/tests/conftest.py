import pytest
from io import StringIO

from tokenizer import Tokenizer
from parser import Parser
from interpreter import Interpreter

@pytest.fixture
def run_dice_code(capsys):
    """
    DICEコードを実行し、標準出力をキャプチャするpytestフィクスチャ。
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
