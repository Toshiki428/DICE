import time
import threading
from concurrent.futures import ThreadPoolExecutor
from parser import Parser, ASTNode, CallNode, ParallelNode, SequentialNode, FuncDefNode, BlockNode, ProgramNode

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


class Interpreter:
    def __init__(self):
        # 関数テーブル
        self.env = {
            'task1': task1,
            'task2': task2,
            'task3': task3,
            'finalize': finalize,
        }

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
            print("main関数の実行...")
            self.visit(node.body)
        else:
            # 将来的には、他の関数定義もここで処理する
            print(f"Function '{node.name}' defined but not called.")

    def visit_BlockNode(self, node):
        for statement in node.statements:
            self.visit(statement)

    def visit_ParallelNode(self, node):
        with ThreadPoolExecutor() as executor:
            # 並列ブロック内のすべてのタスクをスレッドプールに投入する
            futures = [executor.submit(self.visit, stmt) for stmt in node.body.statements]

    def visit_SequentialNode(self, node):
        for sub_node in node.nodes:
            self.visit(sub_node)

    def visit_CallNode(self, node):
        func_name = node.callee.name
        if func_name in self.env:
            args = [self.visit(arg) for arg in node.args]
            self.env[func_name](*args)
        else:
            raise NameError(f"Function '{func_name}' is not defined.")

    def visit_IdentifierNode(self, node):
        if node.name in self.env:
            return self.env[node.name]
        else:
            raise NameError(f"Variable '{node.name}' is not defined.")

    def visit_StringLiteralNode(self, node):
        return node.value

    def visit_NumberLiteralNode(self, node):
        return node.value
