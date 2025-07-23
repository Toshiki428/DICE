# DICE 構文仕様（初期案）

- 並列処理を行いたいときは `parallel { ... }` または `p { ... }` を使う
- `parallel` ブロック内にある処理は、すべて同時に実行される
- 順番に処理を実行したい場合は `->` を使って明示的に書く
- 並列ブロックの中でも `->` を使って順序を表現できる（並列と順次の組み合わせが可能）
- 並列や順次のブロックは入れ子にして使うことができる
- `main()` 関数からプログラムが始まる
- 複数のオブジェクトにまたがる処理を並列化しつつ、段階的に進めたい場合は `parallelTasks(A(), B())` を使う
- `parallelTasks` で作ったグループは `.next()` を使うことで、各オブジェクトのメソッドを段階的に実行できる
- `.next()` は全オブジェクトの同一ステップが終わったら次に進む（暗黙的に同期される）
- 並列ブロックに無限ループや未完了の処理が含まれる可能性はあるが、エラーハンドリングやタイムアウトは今後の設計で詰める予定

## 1. 並列処理の基本構文

```dice
parallel {
	readSensor();
	updateDisplay();
	sendData();
}
```

または省略形：

```dice
p {
	readSensor();
	updateDisplay();
	sendData();
}
```

- `parallel {}`：ブロック内の処理を並列実行

## 2. 順次処理の明示

```dice
loadImage() -> processImage() -> saveImage();
```

- `->` を使うことで**処理順序を明示**。並列ブロック内でも使える。

```dice
parallel {
	fetchData();
	cleanData() -> analyzeData();  // この2つは順番に実行
}
```

## 3. 入れ子構造（ネスト対応）

```dice
main() {
	p {
		task1();
		p {
			subtask1();
			subtask2();
		}
	}
	-> finalize();
}
```

## 4. 並列タスクグループ + 同期制御（試案）

```dice
group = parallelTasks(DeviceA(), DeviceB());
group.next();  // DeviceA.step1(), DeviceB.step1() を同時に実行
group.next();  // DeviceA.step2(), DeviceB.step2() を同時に実行
```

- クラスのメソッド実行を段階的に並列化可能
- `DeviceA` / `DeviceB` はそれぞれ `.stepN()` のような順序を持つオブジェクト想定

## 5. 並列の中に順次、順次の中に並列

```dice
p {
	task1();
	task2() -> task3();
    task3() -> p {
		sub1();
		sub2() -> sub3();
    }
}
```

- どのブロックでも`p{}`と`->`は組み合わせて使用可能

## 6. 明示的な待ち・完了検出（将来的に拡張）

```dice
p {
	waitForNetwork();
	syncTime();
} -> beginMainLoop();
```

- `wait` や `timeout` 構文は今後の拡張ポイントとして設計検討中

## 7. main 関数とプログラムのエントリーポイント

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
