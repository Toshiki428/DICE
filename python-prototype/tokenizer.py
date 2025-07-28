import re
from collections import namedtuple

Token = namedtuple('Token', ['type', 'value', 'line', 'column'])

def tokenize_generator(code):
    """
    ソースコードをトークンに分割するジェネレータ関数
    """
    token_specification = [
        ('NUMBER',        r'\d+(\.\d*)?'),
        ('STRING',        r'"[^"\\]*(\\.[^"\\]*)*"'),
        ('PARALLEL',      r'\bparallel\b'),
        ('P_ALIAS',       r'\bp\b'),
        ('FUNC',          r'\bfunc\b'),
        ('PARALLEL_TASKS',r'\bparallelTasks\b'),
        ('TASKUNIT',      r'\btaskunit\b'),
        ('RETURN',        r'\breturn\b'),
        ('ARROW',         r'->'),
        ('LBRACE',        r'\{'),
        ('RBRACE',        r'\}'),
        ('LPAREN',        r'\('),
        ('RPAREN',        r'\)'),
        ('DOT',           r'\.'),
        ('COMMA',         r','),
        ('SEMICOLON',     r';'),
        ('ASSIGN',        r'='),
        ('COMMENT',       r'//[^\n]*'),
        ('PLUS',          r'\+'),
        ('MINUS',         r'-'),
        ('MULTIPLY',      r'\*'),
        ('DIVIDE',        r'/'),
        ('IDENTIFIER',    r'[A-Za-z_][A-Za-z0-9_]*'),
        ('NEWLINE',       r'\n'),
        ('WHITESPACE',    r'[ \t]+'),
        ('MISMATCH',      r'.'),
    ]
    tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)

    line_num = 1    # コードの行番号
    line_start = 0  # 現在の行の開始位置（行番号を計算するためのインデックス）
    for mo in re.finditer(tok_regex, code):
        kind = mo.lastgroup # マッチした名前の取得（'PARALLEL', 'P_ALIAS' など）
        value = mo.group()  # マッチした文字列の取得（'parallel', 'p' など）
        column = mo.start() - line_start + 1

        if kind == 'WHITESPACE' or kind == 'COMMENT':
            continue
        elif kind == 'NEWLINE':
            line_num += 1
            line_start = mo.end()
            continue
        elif kind == 'MISMATCH':
            raise RuntimeError(f'Unexpected character: {value!r} on line {line_num} column {column}')
        
        yield Token(kind, value, line_num, column)

class Tokenizer:
    def __init__(self, code):
        self.code = code
        self.tokens = []

    def tokenize(self):
        # ジェネレータからトークンのリストを作成
        self.tokens = list(tokenize_generator(self.code))
        return self.tokens
