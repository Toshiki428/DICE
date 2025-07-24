import argparse
from tokenizer import Tokenizer
from parser import Parser
from interpreter import Interpreter

def main():
    # コマンドライン引数のパーサーを設定
    arg_parser = argparse.ArgumentParser(description='DICE Language Interpreter')
    arg_parser.add_argument('file', type=str, help='Path to the DICE source file to execute')
    args = arg_parser.parse_args()

    file_path = args.file
    print(f"--- Reading DICE source file: {file_path} ---")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at '{file_path}'")
        return

    # メインの処理を実行
    try:
        # 1. 字句解析
        print("\n1. Tokenizing...")
        tokenizer = Tokenizer(code)
        tokens = tokenizer.tokenize()

        # 2. 構文解析
        print("\n2. Parsing...")
        parser = Parser(tokens)
        ast = parser.parse()
        print("--- AST ---")
        print(ast)

        # 3. 実行
        print("\n3. Interpreting...")
        interpreter = Interpreter()
        interpreter.visit(ast)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
