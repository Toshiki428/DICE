from tokenizer import Tokenizer, Token

SPACE = ' ' * 4

# --- AST Node Classes ---

class ASTNode:
    """すべてのASTノードの基本クラス"""
    def __repr__(self):
        return self.pretty_print()

    def pretty_print(self, indent=0):
        return SPACE * indent + self.__class__.__name__

class ProgramNode(ASTNode):
    """ASTのルートで、ステートメントのリストを含む"""
    def __init__(self, statements):
        self.statements = statements

    def pretty_print(self, indent=0):
        indent_str = SPACE * indent
        statements_str = "\n".join([s.pretty_print(indent + 1) for s in self.statements])
        return f"{indent_str}ProgramNode(\n{statements_str}\n{indent_str})"

class StatementsNode(ASTNode):
    """ブロックなどの一連のステートメントを表す"""
    def __init__(self, statements):
        self.statements = statements

    def pretty_print(self, indent=0):
        indent_str = SPACE * indent
        statements_str = "\n".join([s.pretty_print(indent + 1) for s in self.statements])
        return f"{indent_str}StatementsNode(\n{statements_str}\n{indent_str})"

class FuncDefNode(ASTNode):
    """関数定義： func name(params) { body }"""
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

    def pretty_print(self, indent=0):
        indent_str = SPACE * indent
        params_str = ", ".join([p.value for p in self.params]) # 引数表示を追加
        return (f"{indent_str}FuncDefNode(name={self.name}, params=[{params_str}],\n"
                f"{self.body.pretty_print(indent + 1)}\n"
                f"{indent_str})")

class TaskUnitDefNode(ASTNode):
    """TaskUnit定義: taskunit name { methods }"""
    def __init__(self, name, methods):
        self.name = name
        self.methods = methods

    def pretty_print(self, indent=0):
        indent_str = SPACE * indent
        methods_str = "\n".join([m.pretty_print(indent + 1) for m in self.methods])
        return (f"{indent_str}TaskUnitDefNode(name={self.name},\n"
                f"{methods_str}\n"
                f"{indent_str})")

class ParallelNode(ASTNode):
    """parallelブロック: p { statements }"""
    def __init__(self, body):
        self.body = body

    def pretty_print(self, indent=0):
        indent_str = SPACE * indent
        return (f"{indent_str}ParallelNode(\n"
                f"{self.body.pretty_print(indent + 1)}\n"
                f"{indent_str})")

class SequenceNode(ASTNode):
    """順次実行記号: a -> b -> c"""
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def pretty_print(self, indent=0):
        indent_str = SPACE * indent
        return (f"{indent_str}SequenceNode(\n"
                f"{self.left.pretty_print(indent + 1)},\n"
                f"{self.right.pretty_print(indent + 1)}\n"
                f"{indent_str})")

class CallNode(ASTNode):
    def __init__(self, callee, args):
        self.callee = callee
        self.args = args

    def pretty_print(self, indent=0):
        indent_str = SPACE * indent
        callee_str = self.callee.pretty_print(0).strip()
        args_str = ", ".join([arg.pretty_print(0) for arg in self.args])
        return (f"{indent_str}CallNode(callee={callee_str}, args=[{args_str}])")

class MemberAccessNode(ASTNode):
    def __init__(self, obj, member):
        self.obj = obj
        self.member = member

    def pretty_print(self, indent=0):
        indent_str = SPACE * indent
        obj_str = self.obj.pretty_print(0).strip()
        return f"{indent_str}MemberAccessNode(obj={obj_str}, member='{self.member.value}')"

class IdentifierNode(ASTNode):
    def __init__(self, token):
        self.token = token
        self.value = token.value

    def pretty_print(self, indent=0):
        return f"{SPACE * indent}IdentifierNode(value='{self.value}')"

class LiteralNode(ASTNode):
    def __init__(self, token):
        self.token = token
        self.value = token.value

    def pretty_print(self, indent=0):
        return f"{SPACE * indent}{self.__class__.__name__}(value={self.value})"

class StringLiteralNode(LiteralNode):
    pass

class NumberLiteralNode(LiteralNode):
    pass

class BooleanLiteralNode(LiteralNode):
    pass

class IfNode(ASTNode):
    """if (condition) { then_branch } else { else_branch }"""
    def __init__(self, condition, then_branch, else_branch):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def pretty_print(self, indent=0):
        indent_str = SPACE * indent
        else_str = ""
        if self.else_branch:
            else_str = (f"\n{indent_str}else\n"
                       f"{self.else_branch.pretty_print(indent + 1)}")

        return (f"{indent_str}IfNode(\n"
                f"{self.condition.pretty_print(indent + 1)},\n"
                f"{self.then_branch.pretty_print(indent + 1)}"
                f"{else_str}\n{indent_str})")

class AssignNode(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def pretty_print(self, indent=0):
        indent_str = SPACE * indent
        return (f"{indent_str}AssignNode(name='{self.name.value}',\n"
                f"{self.value.pretty_print(indent + 1)}\n"
                f"{indent_str})")

class BinaryOpNode(ASTNode):
    """二項演算子を表すノード (例: a + b)"""
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator # Tokenオブジェクト
        self.right = right

    def pretty_print(self, indent=0):
        indent_str = SPACE * indent
        return (f"{indent_str}BinaryOpNode(operator='{self.operator.value}',\n"
                f"{self.left.pretty_print(indent + 1)},\n"
                f"{self.right.pretty_print(indent + 1)}\n"
                f"{indent_str})")

class ReturnNode(ASTNode):
    """return文を表すノード"""
    def __init__(self, value):
        self.value = value

    def pretty_print(self, indent=0):
        indent_str = SPACE * indent
        return (f"{indent_str}ReturnNode(\n"
                f"{self.value.pretty_print(indent + 1)}\n"
                f"{indent_str})")

class TimedNode(ASTNode):
    """@timedアノテーションを表すノード"""
    def __init__(self, node, tag=None):
        self.node = node
        self.tag = tag

    def pretty_print(self, indent=0):
        indent_str = SPACE * indent
        tag_str = f", tag='{self.tag}'" if self.tag else ""
        return (f"{indent_str}TimedNode(node=\n"
                f"{self.node.pretty_print(indent + 1)}\n"
                f"{indent_str}{tag_str})")

# --- Parser Class ---

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def parse(self):
        """プログラム全体を解析し、ASTのルートノードを返す"""
        statements = []
        while not self.at_end():
            statements.append(self.parse_statement())
            if self.peek().type == 'NEWLINE':
                self.consume('NEWLINE')
        return ProgramNode(statements)

    def parse_statement(self):
        """単一のステートメント（文）を解析する"""
        if self.peek().type == 'AT':
            return self.parse_timed_block()
        if self.peek().type == 'FUNC':
            return self.parse_func_def()
        if self.peek().type == 'TASKUNIT':
            return self.parse_task_unit_def()
        if self.peek().type == 'IF':
            return self.parse_if_statement()
        if self.peek().type == 'RETURN':
            return self.parse_return_statement()
        return self.parse_expression_statement()

    def parse_expression_statement(self):
        """式文（値を持つ文）を解析する"""
        expr = self.parse_expression()
        if self.peek().type == 'SEMICOLON':
            self.consume('SEMICOLON')
        return expr

    def parse_return_statement(self):
        """return文を解析する"""
        self.consume('RETURN')
        value = self.parse_expression()
        if self.peek().type == 'SEMICOLON':
            self.consume('SEMICOLON')
        return ReturnNode(value)

    def parse_expression(self):
        """任意の式を解析する（現在は代入式から開始）"""
        return self.parse_assignment()

    def parse_assignment(self):
        """代入式 `a = b` を解析する"""
        if self.peek().type == 'IDENTIFIER' and self.peek(1).type == 'ASSIGN':
            name = IdentifierNode(self.consume('IDENTIFIER'))
            self.consume('ASSIGN')
            value = self.parse_assignment() # 右結合
            return AssignNode(name, value)
        return self.parse_comparison()

    def parse_comparison(self):
        """比較演算 (`==`, `!=`, `<`, `>`, `<=`, `>=`) を解析する"""
        node = self.parse_addition_subtraction()
        while self.peek().type in ('EQ', 'NEQ', 'LT', 'GT', 'LTE', 'GTE'):
            operator = self.consume(self.peek().type)
            right = self.parse_addition_subtraction()
            node = BinaryOpNode(node, operator, right)
        return node

    def parse_sequence(self):
        """`->` を使った順次実行の式を解析する"""
        node = self.parse_addition_subtraction()
        while self.peek().type == 'ARROW':
            self.consume('ARROW')
            right = self.parse_addition_subtraction()
            node = SequenceNode(node, right)
        return node

    def parse_addition_subtraction(self):
        """加算・減算 (`+`, `-`) を解析する"""
        node = self.parse_multiplication_division()
        while self.peek().type in ('PLUS', 'MINUS'):
            operator = self.consume(('PLUS', 'MINUS'))
            right = self.parse_multiplication_division()
            node = BinaryOpNode(node, operator, right)
        return node

    def parse_multiplication_division(self):
        """乗算・除算 (`*`, `/`) を解析する"""
        node = self.parse_call_or_primary()
        while self.peek().type in ('MULTIPLY', 'DIVIDE'):
            operator = self.consume(('MULTIPLY', 'DIVIDE'))
            right = self.parse_call_or_primary()
            node = BinaryOpNode(node, operator, right)
        return node

    def parse_call_or_primary(self):
        """関数呼び出し、メンバーアクセス、またはプライマリ式を解析する"""
        node = self.parse_primary()
        while True:
            if self.peek().type == 'LPAREN':
                node = self.parse_call(node)
            elif self.peek().type == 'DOT':
                self.consume('DOT')
                member = self.consume('IDENTIFIER')
                node = MemberAccessNode(node, member)
            else:
                break
        return node

    def parse_primary(self):
        """最も基本的な式の要素（リテラル、識別子、括弧付きの式など）を解析する"""
        token = self.peek()
        if token.type in ('PARALLEL', 'P_ALIAS'):
            return self.parse_parallel_block()
        elif token.type == 'IDENTIFIER':
            return IdentifierNode(self.consume('IDENTIFIER'))
        elif token.type == 'STRING':
            return StringLiteralNode(self.consume('STRING'))
        elif token.type == 'NUMBER':
            return NumberLiteralNode(self.consume('NUMBER'))
        elif token.type == 'TRUE':
            return BooleanLiteralNode(self.consume('TRUE'))
        elif token.type == 'FALSE':
            return BooleanLiteralNode(self.consume('FALSE'))
        elif token.type == 'PARALLEL_TASKS':
            return IdentifierNode(self.consume('PARALLEL_TASKS'))
        elif token.type == 'LPAREN':
            self.consume('LPAREN')
            expr = self.parse_expression()
            self.consume('RPAREN')
            return expr
        raise SyntaxError(f"Unexpected token {token} at line {token.line}")

    def parse_call(self, callee):
        """関数呼び出し `(args)` を解析する"""
        self.consume('LPAREN')
        args = []
        if self.peek().type != 'RPAREN':
            args.append(self.parse_expression())
            while self.peek().type == 'COMMA':
                self.consume('COMMA')
                args.append(self.parse_expression())
        self.consume('RPAREN')
        return CallNode(callee, args)

    def parse_block(self):
        """`{ ... }` のブロックを解析する"""
        self.consume('LBRACE')
        statements = []
        while self.peek().type != 'RBRACE' and not self.at_end():
            statements.append(self.parse_statement())
            if self.peek().type == 'NEWLINE':
                self.consume('NEWLINE')
        self.consume('RBRACE')
        return StatementsNode(statements)

    def parse_parallel_block(self):
        """`parallel` または `p` ブロックを解析する"""
        self.consume(('PARALLEL', 'P_ALIAS'))
        body = self.parse_block()
        return ParallelNode(body)

    def parse_func_def(self):
        """`func` キーワードから始まる関数定義を解析する"""
        self.consume('FUNC')
        name = self.consume('IDENTIFIER').value
        self.consume('LPAREN')
        
        params = []
        if self.peek().type == 'IDENTIFIER':
            params.append(self.consume('IDENTIFIER'))
            while self.peek().type == 'COMMA':
                self.consume('COMMA')
                params.append(self.consume('IDENTIFIER'))

        self.consume('RPAREN')
        body = self.parse_block()
        return FuncDefNode(name, params, body)

    def parse_if_statement(self):
        self.consume('IF')
        self.consume('LPAREN')
        condition = self.parse_expression()
        self.consume('RPAREN')
        then_branch = self.parse_block()
        else_branch = None
        if self.peek().type == 'ELSE':
            self.consume('ELSE')
            else_branch = self.parse_block()
        return IfNode(condition, then_branch, else_branch)

    def parse_timed_block(self):
        """`@timed` アノテーションが付いたブロックや関数を解析する"""
        self.consume('AT')
        if self.peek().type == 'IDENTIFIER' and self.peek().value == 'timed':
            self.consume('IDENTIFIER')
            
            tag = None
            if self.peek().type == 'LPAREN':
                self.consume('LPAREN')
                if self.peek().type == 'STRING':
                    tag = self.consume('STRING').value.strip('"')
                else:
                    raise SyntaxError(f"Expected string literal for @timed tag, but found {self.peek().type}")
                self.consume('RPAREN')

            # `@timed` の後に続くノードを解析
            if self.peek().type == 'LBRACE':
                # @timed { ... } の形式
                node = self.parse_block()
            elif self.peek().type in ('PARALLEL', 'P_ALIAS'):
                # @timed parallel { ... } の形式
                node = self.parse_parallel_block()
            else:
                # @timed statement; の形式 (例: @timed func_call();)
                node = self.parse_expression_statement()
            return TimedNode(node, tag)
        else:
            raise SyntaxError(f"Expected 'timed' after '@', but found {self.peek().value}")

    def parse_task_unit_def(self):
        """`taskunit` 定義を解析する"""
        self.consume('TASKUNIT')
        name = self.consume('IDENTIFIER').value
        self.consume('LBRACE')
        methods = []
        while self.peek().type != 'RBRACE' and not self.at_end():
            if self.peek().type == 'IDENTIFIER' and self.peek(1).type == 'LPAREN':
                methods.append(self.parse_task_unit_method())
            if self.peek().type == 'NEWLINE':
                self.consume('NEWLINE')
        self.consume('RBRACE')
        return TaskUnitDefNode(name, methods)

    def parse_task_unit_method(self):
        """`taskunit` 内のメソッド定義を解析する"""
        name = self.consume('IDENTIFIER').value
        self.consume('LPAREN')
        # taskunitメソッドの引数はまだサポートしない
        self.consume('RPAREN')
        body = self.parse_block()
        return FuncDefNode(name, [], body) # paramsを空リストで渡している

    # --- Utility Methods ---

    def peek(self, offset=0):
        """先読みして、現在の位置からオフセット分離れたトークンを返す"""
        if self.pos + offset < len(self.tokens):
            return self.tokens[self.pos + offset]
        return Token('EOF', '', -1, -1)

    def consume(self, expected_type):
        """現在のトークンが期待する型であれば消費して進め、そうでなければエラーを発生させる"""
        token = self.peek()
        if isinstance(expected_type, str) and token.type == expected_type:
            self.pos += 1
            return token
        if isinstance(expected_type, tuple) and token.type in expected_type:
            self.pos += 1
            return token
        
        expected_str = f"one of {expected_type}" if isinstance(expected_type, tuple) else expected_type
        raise SyntaxError(
            f"Expected {expected_str} but found {token.type} with value '{token.value}' "
            f"at line {token.line}, column {token.column}"
        )

    def at_end(self):
        """トークンの終端に達したかを判定する"""
        return self.peek().type == 'EOF'
