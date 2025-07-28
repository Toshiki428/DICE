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

## 2. 順次処理の明示

- `->` を使うことで**処理順序を明示**。並列ブロック内でも使える。

```dice
loadImage() -> processImage() -> saveImage();

parallel {
	fetchData();
	cleanData() -> analyzeData();  // この2つは順番に実行
}
```

## 3. 処理時間計測（@timed アノテーション）

- 関数やブロックに `@timed` を付けると、直後のノードの実行時間が計測・レポートされる。
- 並列処理内で個別の処理時間と合計の処理時間を把握するのに有効。

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

```
[TIMED: function] 0.1050s
[TIMED: block]    0.1101s
[TIMED: parallel] 0.0348s
```

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

```
[TIMED: tagA] 0.1050s
[TIMED: tagB] 0.1101s
[TIMED: tagC] 0.0348s
```

## 4. 並列タスクグループ + 同期制御（試案）

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

## 7. 今後の拡張ポイント

- タイムアウト、エラーハンドリング、待機（`wait`）構文の追加を検討中。
- 無限ループや未完了処理の検出と安全な制御を設計する。
