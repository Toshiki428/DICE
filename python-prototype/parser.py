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

class TaskUnitDefNode(ASTNode):
    def __init__(self, name, methods):
        self.name = name
        self.methods = methods

    def pretty_print(self, indent=0):
        indent_str = SPACE * indent
        methods_str = "\n".join([m.pretty_print(indent + 1) for m in self.methods])
        return (f"{indent_str}TaskUnitDefNode(name={self.name},\n"
                f"{methods_str}\n"
                f"{indent_str})")

class TaskUnitMethodNode(ASTNode):
    def __init__(self, name, body):
        self.name = name
        self.body = body

    def pretty_print(self, indent=0):
        indent_str = SPACE * indent
        return (f"{indent_str}TaskUnitMethodNode(name={self.name},\n"
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
        callee_str = self.callee.pretty_print(0).strip() # Callee は IdentifierNode か MemberAccessNode
        args_str = ", ".join([arg.pretty_print(0) for arg in self.args])
        return (f"{indent_str}CallNode(\n"
                f"{indent_str}{SPACE}callee={callee_str},\n"
                f"{indent_str}{SPACE}args=[{args_str}]\n"
                f"{indent_str})")

class MemberAccessNode(ASTNode):
    def __init__(self, obj, member):
        self.obj = obj
        self.member = member

    def pretty_print(self, indent=0):
        indent_str = SPACE * indent
        return f"{indent_str}MemberAccessNode(obj={self.obj.pretty_print(0)}, member='{self.member}')"

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

class AssignNode(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def pretty_print(self, indent=0):
        indent_str = SPACE * indent
        return (f"{indent_str}AssignNode(name='{self.name}',\n"
                f"{self.value.pretty_print(indent + 1)}\n"
                f"{indent_str})")

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
        if self.peek().type == 'TASKUNIT':
            return self.parse_task_unit_def()
        
        # 代入文の可能性をチェック（IDENTIFIER ASSIGN ...）
        if self.peek().type == 'IDENTIFIER' and self.peek(1).type == 'ASSIGN':
            stmt = self.parse_assignment()
            if self.peek().type == 'SEMICOLON':
                self.consume('SEMICOLON')
            return stmt
        
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

    def parse_task_unit_def(self):
        self.consume('TASKUNIT')
        name = self.consume('IDENTIFIER').value
        self.consume('LBRACE')
        methods = []
        while self.peek().type != 'RBRACE':
            methods.append(self.parse_task_unit_method())
        self.consume('RBRACE')
        return TaskUnitDefNode(name, methods)

    def parse_task_unit_method(self):
        name = self.consume('IDENTIFIER').value
        self.consume('LPAREN')
        self.consume('RPAREN')
        body = self.parse_block()
        return TaskUnitMethodNode(name, body)

    def parse_block(self):
        self.consume('LBRACE')
        statements = []
        while self.peek().type != 'RBRACE':
            statements.append(self.parse_statement())
        self.consume('RBRACE')
        return BlockNode(statements)

    def parse_assignment(self):
        name = self.consume('IDENTIFIER').value
        self.consume('ASSIGN')
        value = self.parse_expression()
        return AssignNode(name, value)

    def parse_expression(self):
        nodes = [self.parse_primary_expression()]
        while self.peek().type == 'ARROW':
            self.consume('ARROW')
            nodes.append(self.parse_primary_expression())
        
        if len(nodes) > 1:
            return SequentialNode(nodes)
        return nodes[0]

    def parse_primary_expression(self):
        left = self.parse_atom()

        while True:
            if self.peek().type == 'LPAREN':
                left = self.parse_call(left)
            elif self.peek().type == 'DOT':
                left = self.parse_member_access(left)
            else:
                break
        return left

    def parse_atom(self):
        token = self.peek()
        if token.type in ('PARALLEL', 'P_ALIAS'):
            return self.parse_parallel_block()
        # parallelTasksの呼び出しを処理
        if token.type == 'PARALLEL_TASKS':
            return self.parse_parallel_tasks()
        if token.type == 'IDENTIFIER':
            return IdentifierNode(self.consume('IDENTIFIER').value)
        elif token.type == 'STRING':
            return StringLiteralNode(self.consume('STRING').value[1:-1])
        elif token.type == 'NUMBER':
            return NumberLiteralNode(float(self.consume('NUMBER').value))
        # カッコで囲まれた式
        elif token.type == 'LPAREN':
            self.consume('LPAREN')
            expr = self.parse_expression()
            self.consume('RPAREN')
            return expr
        raise SyntaxError(f"Unexpected token {token}")

    def parse_call(self, callee_node):
        self.consume('LPAREN')
        args = []
        if self.peek().type != 'RPAREN':
            args.append(self.parse_argument())
            while self.peek().type == 'COMMA':
                self.consume('COMMA')
                args.append(self.parse_argument())
        self.consume('RPAREN')
        return CallNode(callee_node, args)

    def parse_argument(self):
        return self.parse_expression()

    def parse_parallel_block(self):
        self.consume(('PARALLEL', 'P_ALIAS'))
        body = self.parse_block()
        return ParallelNode(body)

    def parse_parallel_tasks(self):
        self.consume('PARALLEL_TASKS')
        self.consume('LPAREN')
        args = []
        if self.peek().type != 'RPAREN':
            args.append(self.parse_argument())
            while self.peek().type == 'COMMA':
                self.consume('COMMA')
                args.append(self.parse_argument())
        self.consume('RPAREN')
        return CallNode(IdentifierNode('parallelTasks'), args)

    def parse_member_access(self, obj):
        self.consume('DOT')
        member = self.consume('IDENTIFIER').value
        return MemberAccessNode(obj, member)

    def peek(self, offset=0):
        """
        次のトークンを返す。EOFトークンがある場合はそれを返す。

        Args:
            offset (int): 現在の位置からのオフセット。デフォルトは0。
        """
        if (self.pos + offset) < len(self.tokens):
            return self.tokens[self.pos + offset]
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
