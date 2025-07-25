import time
import random

def dice_print(*args):
  """
  与えられた引数をコンソールに表示する。
  """
  print(*args)

def dice_wait(seconds):
  """
  指定された秒数だけ待機する。
  """
  time.sleep(seconds)

def mock_sensor(name="unknown", delay=1.0):
    """
    モックセンサーの値を生成し、指定された名前と遅延時間で表示する。
    """
    time.sleep(delay)
    value = round(random.uniform(0, 100), 2)
    print(f"[{name}] センサー値: {value}")
    return value
