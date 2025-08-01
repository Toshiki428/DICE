# DICE - Designable, Intuitive, Concurrent Execution

DICE は、IoTやリアルタイム制御などの分野で必要となる並列処理を、直感的かつ安全に記述できることを第一に設計されたプログラミング言語です。

## 背景と目的

- 現在の並列処理の記述は、非同期・コールバック・スレッド管理など複雑で習得コストが高い
- IoT、センサー制御、複数のアクションを同時に扱うロボット制御などでは、**並列性を安全に表現する手段**が求められている
- DICE は、「構造化された並列性」と「実行時間の可視化」を言語レベルでサポートすることで、**リアルタイム性と設計しやすさの両立**を目指す

## セットアップ

本プロトタイプはPythonで実装されています。実行にはPython 3.6以上が必要です。

1. リポジトリをクローンします。
```bash
git clone https://github.com/Toshiki428/DICE.git
cd DICE
```

2. （推奨）仮想環境を作成して有効化します。
```bash
python3 -m venv venv
source venv/bin/activate
```

現時点では、追加の依存ライブラリはありません。

## 使い方

`python-prototype/main.py` を使って、`.dice` ファイルを実行します。

```bash
python python-prototype/main.py <ファイルパス>
```

### サンプルコードの実行

`examples/` ディレクトリに、DICEの主な機能を示すサンプルコードが用意されています。ファイル名の数字が大きくなるにつれて、応用的な内容になっています。

例えば、並列処理と順次処理を学ぶには `02_parallel_and_sequence.dice` を実行します。

```bash
$ python python-prototype/main.py examples/02_parallel_and_sequence.dice

1. Tokenizing...

2. Parsing...
--- AST ---
ProgramNode(
    StatementsNode(
        FuncDefNode(name=main, params=[],
            StatementsNode(
                SequenceNode(
                    ParallelNode(
                        StatementsNode(
                            CallNode(callee=IdentifierNode(value='print'), args=[StringLiteralNode(value="task1: 並列実行")]),
                            SequenceNode(
                                CallNode(callee=IdentifierNode(value='print'), args=[StringLiteralNode(value="task2: これはtask3の前に実行")]),
                                CallNode(callee=IdentifierNode(value='print'), args=[StringLiteralNode(value="task3: これはtask2の後に実行")])
                            )
                        )
                    ),
                    CallNode(callee=IdentifierNode(value='print'), args=[StringLiteralNode(value="finalize: 全ての並列処理が終わった後に実行")])
                ),
                CallNode(callee=IdentifierNode(value='print'), args=[StringLiteralNode(value="-----")]),
                SequenceNode(
                    ParallelNode(
                        StatementsNode(
                            CallNode(callee=IdentifierNode(value='mock_sensor'), args=[StringLiteralNode(value="温度センサー"), NumberLiteralNode(value=1)]),
                            CallNode(callee=IdentifierNode(value='mock_sensor'), args=[StringLiteralNode(value="湿度センサー"), NumberLiteralNode(value=0.5)])
                        )
                    ),
                    CallNode(callee=IdentifierNode(value='print'), args=[StringLiteralNode(value="センサーデータの取得完了")])
                )
            )
        )
    )
)

3. Interpreting...
task2: これはtask3の前に実行
task1: 並列実行
task3: これはtask2の後に実行
finalize: 全ての並列処理が終わった後に実行
-----
[湿度センサー] センサー値: 42.12
[温度センサー] センサー値: 89.34
センサーデータの取得完了
```

時間計測機能を試すには、`05_timed_annotation.dice` を実行します。

```bash
$ python python-prototype/main.py examples/05_timed_annotation.dice
```


## 特徴（プロトタイプで実装済み）

- **明示的な並列処理構文**： `parallel { ... }` または短縮形 `p { ... }`
- **順次実行の依存関係表現**： `a() -> b()` のように明示的に記述
- **実行時間計測**： `@timed` アノテーションで特定処理の時間を測定・出力
- **条件分岐とループ構文のサポート**： `if`, `loop`, `p loop` に対応
- 並列オブジェクト（`parallelTasks`）の`next()`による段階的同期制御

## 実装予定・今後の拡張

- 型システム（静的型チェックや構造化型の導入）
- リスト・辞書などのコレクション型
- エディタ補完やビジュアルデバッガ連携（開発支援ツール）


## 開発者向け情報 (For Developers)

### 実行ファイルのビルド

DICEインタプリタを単一の実行ファイルとしてビルドすることができます。  
ビルド作業にはPythonと`PyInstaller`が必要ですが、一度ビルドすれば、Pythonがインストールされていない環境でもDICEプログラムを実行できる単一ファイルが生成されます。

1. `PyInstaller` をインストールします。
    ```bash
    pip install pyinstaller
    ```

2. 以下のコマンドでビルドを実行します。
    ```bash
    (cd python-prototype && pyinstaller dice.spec)
    ```

3.  ビルドが成功すると、`python-prototype/dist/` ディレクトリに `dice` という名前の実行ファイルが生成されます。  
    プロジェクトのルートディレクトリから、以下のコマンドでプログラムを実行します。
    ```bash
    ./python-prototype/dist/dice <ファイルパス>
    ```
