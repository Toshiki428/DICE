# DICE - Designable, Intuitive, Concurrent Execution

DICE は、「並列処理を直感的かつ安全に書ける」ことを目的としたプログラミング言語です。

## 背景と目的

- 現在の並列処理記述は複雑で習得コストが高い
- IoTやセンサーデータのリアルタイム制御など、並列性が重要な分野において、それをもっと簡潔に記述したい

## 特徴（MVP予定）

- `parallel { ... }` 構文による明示的な並列処理
- 関数呼び出しの順次指定構文（`->`）による直感的な依存関係定義
- 並列オブジェクトの`next()`による同期タイミング制御
