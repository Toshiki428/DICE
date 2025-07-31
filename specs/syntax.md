# DICE 構文仕様

- 並列処理を行いたいときは `parallel { ... }` または `p { ... }` を使う
- `parallel` ブロック内にある処理は、すべて並列で実行される
- 関数直下では順次実行される
- `parallel` ブロックの中でも `->` を使って順序を表現できる（並列と順次の組み合わせが可能）
- 並列ブロックや順次表現は入れ子にして使うことができる
- `main()` 関数からプログラムが始まる
- `@timed` アノテーションで関数の処理の実行時間計測が可能
- 複数のオブジェクトにまたがる処理を並列化しつつ、段階的に進めたい場合は `parallelTasks(A(), B())` を使う
- `parallelTasks` で作ったグループは `.next()` を使うことで、各オブジェクトのメソッドを段階的に実行できる
- `.next()` は全オブジェクトの同一ステップが終わったら次に進む（暗黙的に同期される）
- 並列ブロックに無限ループや未完了の処理が含まれる可能性はあるが、エラーハンドリングやタイムアウトは今後の設計で詰める予定

## 1. 並列処理の基本構文

- 並列処理を行いたいときは、 `parallel` ブロックを使う。

```dice
parallel {
	readSensor();
	updateDisplay();
	sendData();
}

// 省略形
p {
	readSensor();
	updateDisplay();
	sendData();
}
```

## 2. 順次処理と式としてのブロック

### 順次実行の明示 (`->`)

`->` 演算子は、処理の実行順序を明示するために使う。

```dice
loadImage() -> processImage() -> saveImage();
```

### 式としてのブロック構文

DICEの `p {}`、`if {}`、`loop {}`、`p loop {}` といったブロックを持つ構文は、単独の「文」としてだけでなく、`->` 演算子で繋ぐことができる「式」の一部としても振る舞う。  
これにより、柔軟な処理フローの記述が可能となる。

**`parallel` ブロックとの組み合わせ:**

`parallel` ブロック全体の完了を待ってから、次の処理を実行させることが可能。

```dice
// まずはAとBを並列で実行し、両方が完了したらCを実行する
p {
    taskA();
    taskB();
} -> taskC();
```

**`if` や `loop` との組み合わせ:**

条件分岐やループ処理の完了をトリガーに、次の処理へ繋げることもできる。

```dice
if (checkStatus()) {
    print("Status OK");
} -> launch();

loop i in 0..5 {
    print(i);
} -> print("Loop finished!");
```

このように、ブロック構文を式として扱える性質が、DICEの直感的な並列・順次制御の核となる。

## 3. 処理時間計測（@timed アノテーション）

- 関数やブロックに `@timed` を付けると、直後のノードの実行時間が計測・レポートされる。
- 並列処理内で個別の処理時間と合計の処理時間を把握するのに有効。

プログラム：
```dice
@timed
loadSensorData();

@timed
{
	loadSensorData1();
	loadSensorData2();
}

@timed
parallel {
    readSensor1();
    readSensor2();
}
```


実行結果：
```
[TIMED: function] 0.1050s
[TIMED: block]    0.1101s
[TIMED: parallel] 0.0348s
```

プログラム：
```dice
@timed("tagA")
loadSensorData();

@timed("tagB")
{
	loadSensorData1();
	loadSensorData2();
}

@timed("tagC")
parallel {
    readSensor1();
    readSensor2();
}
```

実行結果：

```
[TIMED: tagA] 0.1050s
[TIMED: tagB] 0.1101s
[TIMED: tagC] 0.0348s
```

将来的にこのような機能も追加予定

```
@timed(detailed=true)  // 全体 + 各子ステップ
p {
    a();
    b() -> c();
}
```

```
[TIMED] ParallelBlock {
    a: 12ms
    b -> c: 5ms -> 6ms
}
Total: 23ms
```

## 4. 並列タスクグループ + 同期制御

- 複数のオブジェクトにまたがる処理を段階的に並列化したい場合に使う。
- `.next()` はすべてのオブジェクトの同じステップが完了したら次に進む（暗黙の同期）。

```dice
taskunit DeviceA {
	step1() { ... }
	step2() { ... }
}

taskunit DeviceB {
	step1() { ... }
	step2() { ... }
}

group = parallelTasks(DeviceA(), DeviceB());
group.next();  // DeviceA.step1(), DeviceB.step1() を並列実行
group.next();  // DeviceA.step2(), DeviceB.step2() を並列実行
```

## 5. 入れ子構造の対応

- 並列ブロック内に順次処理、順次処理内に並列ブロックを入れることが可能。

```dice
p {
	task1();
	task2() -> task3();
	task3() -> p {
		subtask1();
		subtask2() -> subtask3();
	}
}
-> finalize();
```

## 6. エントリーポイント

- プログラムは `main()` 関数から開始する。

```dice
func main() {
	initialize();
	p {
		startSensors();
		listenButton();
	}
	-> shutdown();
}
```
