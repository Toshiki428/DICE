import re
from collections import namedtuple

Token = namedtuple('Token', ['type', 'value'])

class Tokenizer:
    def __init__(self, code):
        self.code = code
        self.tokens = []
        self.current_pos = 0

    def tokenize(self):
        token_specification = [
            ('NUMBER',        r'\d+(\.\d*)?'),
            ('STRING',        r'"[^"\\]*(\\.[^"\\]*)*"'),
            ('PARALLEL',      r'\bparallel\b'),
            ('P_ALIAS',       r'\bp\b'),
            ('FUNC',          r'\bfunc\b'),
            ('PARALLEL_TASKS',r'\bparallelTasks\b'),
            ('ARROW',         r'->'),
            ('LBRACE',        r'\{'),
            ('RBRACE',        r'\}'),
            ('LPAREN',        r'\('),
            ('RPAREN',        r'\)'),
            ('DOT',           r'\.'),
            ('COMMA',         r','),
            ('SEMICOLON',     r';'),
            ('IDENTIFIER',    r'[A-Za-z_][A-Za-z0-9_]*'),
            ('NEWLINE',       r'\n'),
            ('WHITESPACE',    r'[ \t]+'),
            ('MISMATCH',      r'.'),
        ]
        tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)

        for mo in re.finditer(tok_regex, self.code):
            kind = mo.lastgroup # マッチした名前の取得（'PARALLEL', 'P_ALIAS' など）
            value = mo.group()  # マッチした文字列の取得（'parallel', 'p' など）
            
            if kind == 'WHITESPACE':
                continue
            elif kind == 'MISMATCH':
                raise RuntimeError(f'Unexpected character: {value!r} on line {self.code.count("\n", 0, mo.start()) + 1}')
            
            # 'p' は単独の識別子としても使われる可能性があるため、文脈で判断が必要だが、
            # ここでは予約語として扱う。より高度なパーサーで区別する。
            # 'main'も同様。
            if kind == 'IDENTIFIER' and value == 'p':
                kind = 'P_ALIAS'
            
            self.tokens.append(Token(kind, value))
            
        return self.tokens
