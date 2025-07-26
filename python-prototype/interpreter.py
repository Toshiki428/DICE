import time
import threading
import inspect
from concurrent.futures import ThreadPoolExecutor
from parser import *
from stdlib import dice_print, dice_wait, mock_sensor

# --- シミュレーション用の関数 ---
def task1():
    print(f"Executing task1 on thread {threading.get_ident()}...")
    time.sleep(1)
    print("task1 finished.")

def task2():
    print(f"Executing task2 on thread {threading.get_ident()}...")
    time.sleep(0.5)
    print("task2 finished.")

def task3():
    print(f"Executing task3 on thread {threading.get_ident()}...")
    time.sleep(0.7)
    print("task3 finished.")

def finalize():
    print(f"Executing finalize on thread {threading.get_ident()}...")
    time.sleep(0.2)
    print("finalize finished.")


class TaskUnit:
    """
    TaskUnitは、`taskunit`の定義を保持するクラス。
    メソッドは、step1, step2, ... のように連番の名前を持つ。
    """
    def __init__(self, name, methods):
        self.name = name
        self.methods = methods
        self.current_step = 1

    def get_method(self, name):
        return self.methods.get(name)

class TaskUnitGroup:
    """
    TaskUnitGroupは、複数のTaskUnitをまとめて管理するクラス。
    """
    def __init__(self, task_units):
        self.task_units = task_units
        self.current_step_index = 1

    def next_step(self, interpreter):
        method_name = f"step{self.current_step_index}"
        executable_methods = []
        for tu in self.task_units:
            method_node = tu.get_method(method_name)
            if method_node:
                executable_methods.append(method_node)

        if not executable_methods:
            print(f"No more step{self.current_step_index} methods to execute in TaskUnitGroup.")
            return

        # ここでinterpreterがInterpreterクラスのインスタンスであることを確認
        if not isinstance(interpreter, Interpreter):
            raise TypeError("Expected an Interpreter instance for execution.")

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(interpreter.visit, method.body) for method in executable_methods]
            for future in futures:
                future.result()
        
        self.current_step_index += 1

class Interpreter:
    def __init__(self):
        # 関数テーブル
        self.env = {
            'task1': task1,
            'task2': task2,
            'task3': task3,
            'finalize': finalize,
            'print': dice_print,
            'wait': dice_wait,
            'mock_sensor': mock_sensor,
        }
        # taskunitの定義を保持（taskunit名: TaskUnitインスタンス）
        self.task_unit_defs = {}

    def visit(self, node):
        method_name = f'visit_{node.__class__.__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise NotImplementedError(f"No visit_{node.__class__.__name__} method defined")

    def visit_ProgramNode(self, node):
        for statement in node.statements:
            self.visit(statement)

    def visit_FuncDefNode(self, node):
        if node.name == 'main':
            self.visit(node.body)
        else:
            # 将来的には、他の関数定義もここで処理する
            print(f"Function '{node.name}' defined but not called.")

    def visit_TaskUnitDefNode(self, node):
        # {step1: TaskUnitMethodNode, step2: TaskUnitMethodNode, ...} のようにメソッドを辞書に格納
        methods = {method.name: method for method in node.methods}
        self.task_unit_defs[node.name] = TaskUnit(node.name, methods)

    def visit_BlockNode(self, node):
        for statement in node.statements:
            self.visit(statement)

    def visit_ParallelNode(self, node):
        with ThreadPoolExecutor() as executor:
            # 並列ブロック内のすべてのタスクをスレッドプールに投入する
            futures = [executor.submit(self.visit, stmt) for stmt in node.body.statements]
            for future in futures:
                future.result()

    def visit_SequentialNode(self, node):
        for sub_node in node.nodes:
            self.visit(sub_node)

    def visit_CallNode(self, node):
        func_name = None

        if isinstance(node.callee, IdentifierNode):
            func_name = node.callee.name
            if func_name not in self.env and func_name != 'parallelTasks':
                raise NameError(f"Function '{func_name}' is not defined.")
            func = self.env.get(func_name) # parallelTasksはenvにないためgetを使う

        elif isinstance(node.callee, MemberAccessNode):
            value = self.visit(node.callee)
            return value
            
        else:
            raise TypeError(f"Unsupported callee type: {type(node.callee)}")

        if func_name == 'parallelTasks':
            task_unit_instances = []
            for arg_node in node.args:
                if isinstance(arg_node, IdentifierNode):
                    task_unit_name = arg_node.name
                    if task_unit_name in self.task_unit_defs:
                        # taskunitの新しいインスタンスを作成
                        task_unit_instances.append(self.task_unit_defs[task_unit_name])
                    else:
                        raise NameError(f"TaskUnit '{task_unit_name}' is not defined.")
                else:
                    raise TypeError("parallelTasks expects taskunit identifiers as arguments.")
            return TaskUnitGroup(task_unit_instances)
        
        # 通常の関数呼び出し
        args = [self.visit(arg) for arg in node.args]

        sig = inspect.signature(func)
        params = sig.parameters

        if len(args) != len(params):
            raise TypeError(f"{func_name}() takes {len(params)} positional arguments but {len(args)} were given")

        func(*args)

    def visit_AssignNode(self, node):
        value = self.visit(node.value)
        self.env[node.name] = value

    def visit_MemberAccessNode(self, node):
        obj = self.visit(node.obj)
        member_name = node.member

        if isinstance(obj, TaskUnitGroup):
            if member_name == 'next':
                obj.next_step(self)
            else:
                raise AttributeError(f"TaskUnitGroup has no attribute '{member_name}'")
        else:
            raise TypeError(f"Object of type {type(obj)} does not support member access.")

    def visit_IdentifierNode(self, node):
        if node.name in self.env:
            return self.env[node.name]
        else:
            raise NameError(f"Variable '{node.name}' is not defined.")

    def visit_StringLiteralNode(self, node):
        return node.value

    def visit_NumberLiteralNode(self, node):
        return node.value
