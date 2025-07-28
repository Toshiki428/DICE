import time
from concurrent.futures import ThreadPoolExecutor
from parser import ASTNode, FuncDefNode, ParallelNode, SequenceNode, CallNode, IdentifierNode, AssignNode, MemberAccessNode, StatementsNode, ProgramNode, TaskUnitDefNode, StringLiteralNode, NumberLiteralNode, BinaryOpNode, ReturnNode, TimedNode
from stdlib import STD_LIB

# --- Custom Exception for Return Values ---
class ReturnValue(Exception):
    """関数の戻り値を伝えるためのカスタム例外"""
    def __init__(self, value):
        self.value = value

# --- Environment for Variables and Functions ---

class Environment:
    """変数や関数のスコープを管理する環境クラス"""
    def __init__(self, outer=None):
        self.outer = outer
        self.values = {}

    def get(self, name):
        if name in self.values:
            return self.values[name]
        if self.outer is not None:
            return self.outer.get(name)
        raise NameError(f"Name '{name}' is not defined.")

    def set(self, name, value):
        self.values[name] = value
        return value

# --- TaskUnit and Grouping ---

class TaskUnit:
    """taskunitの定義を表すクラス"""
    def __init__(self, definition_node):
        self.definition_node = definition_node
        self.methods = {m.name: m for m in definition_node.methods}

class TaskUnitInstance:
    """taskunitのインスタンス。実行状態を持つ"""
    def __init__(self, task_unit_class):
        self.task_unit_class = task_unit_class
        self.step = 0

    def get_method_for_step(self):
        method_name = f"step{self.step + 1}"
        return self.task_unit_class.methods.get(method_name)

class ParallelTaskGroup:
    """parallelTasksで作成されたTaskUnitインスタンスのグループ"""
    def __init__(self, instances):
        self.instances = instances

    def next(self, interpreter, env):
        """グループ内の全インスタンスの次のステップを並列実行する"""
        with ThreadPoolExecutor() as executor:
            futures = []
            for instance in self.instances:
                method_node = instance.get_method_for_step()
                if method_node:
                    # 各メソッドを新しい環境で実行
                    future = executor.submit(interpreter.visit, method_node.body, Environment(outer=env))
                    futures.append(future)
            
            # すべてのタスクの完了を待つ
            for future in futures:
                future.result()

        # ステップを進める
        for instance in self.instances:
            instance.step += 1

# --- Member Method Wrapper ---

class MemberMethodWrapper:
    """メンバーアクセスされたメソッドをラップし、呼び出し時に必要な引数を渡す"""
    def __init__(self, obj, method_name, interpreter_instance, env):
        self.obj = obj
        self.method_name = method_name
        self.interpreter_instance = interpreter_instance
        self.env = env

    def __call__(self, *args):
        if self.method_name == 'next':
            # ParallelTaskGroupのnextメソッドはinterpreterとenvを必要とする
            return self.obj.next(self.interpreter_instance, self.env)
        # 他のメンバーメソッドが追加された場合、ここにロジックを追加
        raise AttributeError(f"Method '{self.method_name}' not supported via direct call.")

# --- Interpreter ---

class Interpreter:
    def __init__(self):
        self.global_env = Environment()
        # 標準ライブラリを登録
        for name, func in STD_LIB.items():
            self.global_env.set(name, func)

    def interpret(self, ast):
        """ASTを受け取り、プログラムを実行する"""
        try:
            self.visit(ast, self.global_env)
        except ReturnValue as e:
            # プログラムのトップレベルでのreturnはエラー
            raise RuntimeError(f"Return statement outside of function: {e.value}")

    def visit(self, node, env):
        """ASTノードを辿り、対応するvisitメソッドを呼び出す"""
        method_name = f'visit_{node.__class__.__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node, env)

    def generic_visit(self, node, env):
        raise NotImplementedError(f"No visit_{node.__class__.__name__} method defined")

    def visit_ProgramNode(self, node, env):
        for stmt in node.statements:
            self.visit(stmt, env)
        # main関数を実行
        main_func = env.get('main')
        if isinstance(main_func, FuncDefNode):
            # main関数の実行はReturnValueを捕捉しない
            self.visit(main_func.body, Environment(outer=env))

    def visit_StatementsNode(self, node, env):
        for stmt in node.statements:
            try:
                self.visit(stmt, env)
            except ReturnValue as e:
                # return文が実行されたら、それ以上ステートメントを処理せずに例外を再スロー
                raise e

    def visit_FuncDefNode(self, node, env):
        env.set(node.name, node)

    def visit_TaskUnitDefNode(self, node, env):
        task_unit_class = TaskUnit(node)
        env.set(node.name, task_unit_class)

    def visit_ParallelNode(self, node, env):
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.visit, stmt, Environment(outer=env)) for stmt in node.body.statements]
            for future in futures:
                future.result() # 各スレッドの完了を待つ

    def visit_SequenceNode(self, node, env):
        self.visit(node.left, env)
        return self.visit(node.right, env)

    def visit_AssignNode(self, node, env):
        value = self.visit(node.value, env)
        env.set(node.name.value, value)
        return value

    def visit_BinaryOpNode(self, node, env):
        left_val = self.visit(node.left, env)
        right_val = self.visit(node.right, env)
        operator_type = node.operator.type

        if operator_type == 'PLUS':
            return left_val + right_val
        elif operator_type == 'MINUS':
            return left_val - right_val
        elif operator_type == 'MULTIPLY':
            return left_val * right_val
        elif operator_type == 'DIVIDE':
            if right_val == 0:
                raise ZeroDivisionError("Division by zero")
            return left_val / right_val
        else:
            raise TypeError(f"Unsupported operator: {node.operator.value}")

    def visit_ReturnNode(self, node, env):
        value = self.visit(node.value, env)
        raise ReturnValue(value)

    def visit_CallNode(self, node, env):
        # parallelTasksの特別な処理を最初にチェック
        if isinstance(node.callee, IdentifierNode) and node.callee.value == 'parallelTasks':
            instances = []
            for arg_node in node.args:
                # parallelTasksの引数はTaskUnitの識別子であると想定
                if isinstance(arg_node, IdentifierNode):
                    task_unit_class = env.get(arg_node.value)
                    if isinstance(task_unit_class, TaskUnit):
                        instances.append(TaskUnitInstance(task_unit_class))
                    else:
                        raise TypeError(f"Argument '{arg_node.value}' to parallelTasks is not a TaskUnit.")
                else:
                    raise TypeError("parallelTasks expects TaskUnit identifiers as arguments.")
            return ParallelTaskGroup(instances)

        # それ以外の通常の関数呼び出しの解決
        callee = self.visit(node.callee, env)
        args = [self.visit(arg, env) for arg in node.args]

        if callable(callee):
            return callee(*args)
        elif isinstance(callee, FuncDefNode):
            # ユーザー定義関数の呼び出し
            func_env = Environment(outer=self.global_env) # クロージャのためglobalを参照
            
            # 引数の数をチェック
            if len(args) != len(callee.params):
                raise TypeError(f"{callee.name}() takes {len(callee.params)} arguments but {len(args)} were given")
            
            # 引数を関数スコープに設定
            for i, param_name_node in enumerate(callee.params):
                func_env.set(param_name_node.value, args[i])

            try:
                self.visit(callee.body, func_env)
            except ReturnValue as e:
                return e.value # ReturnValue例外から値を取り出して返す
            return None # return文がない場合はNoneを返す
        else:
            # エラーメッセージの修正: MemberAccessNodeの場合も考慮
            callee_name = node.callee.value if isinstance(node.callee, IdentifierNode) else str(node.callee)
            raise TypeError(f"'{callee_name}' is not a function or callable.")

    def visit_MemberAccessNode(self, node, env):
        obj = self.visit(node.obj, env)
        member_name = node.member.value

        if isinstance(obj, ParallelTaskGroup):
            if member_name == 'next':
                # MemberMethodWrapperを返すように変更
                return MemberMethodWrapper(obj, member_name, self, env)
            else:
                raise AttributeError(f"ParallelTaskGroup has no attribute '{member_name}'")
        else:
            raise TypeError(f"Object of type {type(obj)} does not support member access: {obj}")

    def visit_TimedNode(self, node, env):
        start_time = time.time()
        result = self.visit(node.node, env)
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # 出力形式の変更
        if node.tag:
            label = node.tag
        elif isinstance(node.node, CallNode):
            label = "function"
        elif isinstance(node.node, StatementsNode):
            label = "block"
        elif isinstance(node.node, ParallelNode):
            label = "parallel"
        else:
            label = node.node.__class__.__name__

        print(f"[TIMED: {label}] {elapsed_time:.4f}s")
        return result

    def visit_IdentifierNode(self, node, env):
        return env.get(node.value)

    def visit_StringLiteralNode(self, node, env):
        return node.value.strip('"')

    def visit_NumberLiteralNode(self, node, env):
        return float(node.value)
