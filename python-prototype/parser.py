from tokenizer import Tokenizer, Token

SPACE = ' ' * 4

class ASTNode:
    def __repr__(self):
        return self.pretty_print()

    def pretty_print(self, indent=0):
        return SPACE * indent + self.__class__.__name__

class ProgramNode(ASTNode):
    def __init__(self, statements):
        self.statements = statements

    def pretty_print(self, indent=0):
        indent_str = SPACE * indent
        statements_str = "\n".join([s.pretty_print(indent + 1) for s in self.statements])
        return f"{indent_str}ProgramNode(\n{statements_str}\n{indent_str})"

class FuncDefNode(ASTNode):
    def __init__(self, name, body):
        self.name = name
        self.body = body

    def pretty_print(self, indent=0):
        indent_str = SPACE * indent
        return (f"{indent_str}FuncDefNode(name={self.name},\n"
                f"{self.body.pretty_print(indent + 1)}\n"
                f"{indent_str})")

class BlockNode(ASTNode):
    def __init__(self, statements):
        self.statements = statements

    def pretty_print(self, indent=0):
        indent_str = SPACE * indent
        statements_str = "\n".join([s.pretty_print(indent + 1) for s in self.statements])
        return f"{indent_str}BlockNode(\n{statements_str}\n{indent_str})"

class ParallelNode(ASTNode):
    def __init__(self, body):
        self.body = body

    def pretty_print(self, indent=0):
        indent_str = SPACE * indent
        return (f"{indent_str}ParallelNode(\n"
                f"{self.body.pretty_print(indent + 1)}\n"
                f"{indent_str})")

class SequentialNode(ASTNode):
    def __init__(self, nodes):
        self.nodes = nodes

    def pretty_print(self, indent=0):
        indent_str = SPACE * indent
        nodes_str = "\n".join([n.pretty_print(indent + 1) for n in self.nodes])
        return f"{indent_str}SequentialNode(\n{nodes_str}\n{indent_str})"

class CallNode(ASTNode):
    def __init__(self, callee, args):
        self.callee = callee
        self.args = args

    def pretty_print(self, indent=0):
        indent_str = SPACE * indent
        args_str = ", ".join([arg.pretty_print(0) for arg in self.args])
        return f"{indent_str}CallNode(callee={self.callee.name!r}, args=[{args_str}])"

class IdentifierNode(ASTNode):
    def __init__(self, name):
        self.name = name

    def pretty_print(self, indent=0):
        indent_str = SPACE * indent
        return f"{indent_str}IdentifierNode(name='{self.name}')"

class StringLiteralNode(ASTNode):
    def __init__(self, value):
        self.value = value

    def pretty_print(self, indent=0):
        indent_str = SPACE * indent
        return f'{indent_str}StringLiteralNode(value="{self.value}")'

class NumberLiteralNode(ASTNode):
    def __init__(self, value):
        self.value = value

    def pretty_print(self, indent=0):
        indent_str = SPACE * indent
        return f'{indent_str}NumberLiteralNode(value={self.value})'


class Parser:
    def __init__(self, tokens):
        self.tokens = [t for t in tokens if t.type != 'NEWLINE'] # NEWLINEトークンを除外
        self.pos = 0

    def parse(self):
        statements = []
        while not self.at_end():
            statements.append(self.parse_statement())
        return ProgramNode(statements)

    def parse_statement(self):
        if self.peek().type == 'FUNC':
            return self.parse_func_def()
        
        expr = self.parse_expression()
        if self.peek().type == 'SEMICOLON':
            self.consume('SEMICOLON')
        return expr

    def parse_func_def(self):
        self.consume('FUNC')
        name = self.consume('IDENTIFIER').value
        self.consume('LPAREN')
        self.consume('RPAREN')
        body = self.parse_block()
        return FuncDefNode(name, body)

    def parse_block(self):
        self.consume('LBRACE')
        statements = []
        while self.peek().type != 'RBRACE':
            statements.append(self.parse_statement())
        self.consume('RBRACE')
        return BlockNode(statements)

    def parse_expression(self):
        nodes = [self.parse_primary_expression()]
        while self.peek().type == 'ARROW':
            self.consume('ARROW')
            nodes.append(self.parse_primary_expression())
        
        if len(nodes) > 1:
            return SequentialNode(nodes)
        return nodes[0]

    def parse_primary_expression(self):
        token = self.peek()
        if token.type in ('PARALLEL', 'P_ALIAS'):
            return self.parse_parallel_block()
        if token.type == 'IDENTIFIER':
            ident = IdentifierNode(self.consume('IDENTIFIER').value)
            if self.peek().type == 'LPAREN':
                self.consume('LPAREN')
                args = []
                if self.peek().type != 'RPAREN':
                    args.append(self.parse_argument())
                    while self.peek().type == 'COMMA':
                        self.consume('COMMA')
                        args.append(self.parse_argument())
                self.consume('RPAREN')
                return CallNode(ident, args)
            return ident
        elif token.type == 'STRING':
            return StringLiteralNode(self.consume('STRING').value[1:-1])
        elif token.type == 'NUMBER':
            return NumberLiteralNode(float(self.consume('NUMBER').value))
        raise SyntaxError(f"Unexpected token {token}")

    def parse_argument(self):
        return self.parse_expression()

    def parse_parallel_block(self):
        self.consume(('PARALLEL', 'P_ALIAS'))
        body = self.parse_block()
        return ParallelNode(body)

    def peek(self):
        """
        次のトークンを返す。EOFトークンがある場合はそれを返す。
        """
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token('EOF', '')

    def consume(self, expected_type):
        """
        期待されるトークンタイプを消費し、そのトークンを返す。
        もし期待されるトークンタイプと異なる場合はSyntaxErrorを発生する。

        Args:
            expected_type (str or tuple): 期待されるトークンのタイプ。
        """
        token = self.peek()
        
        is_match = False
        if isinstance(expected_type, tuple):
            if token.type in expected_type:
                is_match = True
        elif token.type == expected_type:
            is_match = True

        if not is_match:
            expected_str = f"one of {expected_type}" if isinstance(expected_type, tuple) else expected_type
            raise SyntaxError(f"Expected {expected_str} but found {token.type} with value '{token.value}'")
        self.pos += 1
        return token

    def at_end(self):
        """
        現在の位置がトークンリストの終端であればTrueを返す。
        """
        return self.peek().type == 'EOF'
