# -*- coding: utf-8 -*-
"""阶段4 亲手参与闭环：用程序证明「阶段3会卡、阶段4不卡」。

原理（心跳检测）：
  在读文件的同时，用 QTimer 每 100ms 往主线程事件队列里插一个「心跳」。
  - 如果主线程被耗时读文件占住 → 事件队列排不了心跳 → 心跳迟到很多 → 判定「卡死」。
  - 如果主线程空闲（读文件丢给工作线程）→ 心跳准时 → 判定「流畅」。

运行：
  .venv\\Scripts\\python.exe 04_thread\\verify_no_freeze.py

输出两张对照：阶段3（主线程直接读）vs 阶段4（QThread 后台读）的最大心跳延迟。
"""
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("QtAgg")
from PySide6.QtCore import QThread, QTimer, Signal
from PySide6.QtWidgets import QApplication

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "01_backend"))
from rd_data import load_rd  # noqa: E402

BIG_FILE = ROOT / "data" / "slow_rd.csv"


class Heartbeat:
    """主线程心跳：每 100ms 记一次实际到达时间，算最大延迟。"""

    def __init__(self, app):
        self.app = app
        self.timer = QTimer()
        self.timer.setInterval(100)
        self.last = time.perf_counter()
        self.max_lag_ms = 0.0
        self.timer.timeout.connect(self._tick)

    def _tick(self):
        now = time.perf_counter()
        lag = (now - self.last - 0.1) * 1000.0   # 实际间隔 - 期望100ms
        self.max_lag_ms = max(self.max_lag_ms, lag)
        self.last = now

    def start(self):
        self.timer.start()

    def stop(self):
        self.timer.stop()


class ReadWorker(QThread):
    """阶段4 用的后台读取线程（和主程序 LoadWorker 同构）。"""
    done = Signal(object)

    def run(self):
        t0 = time.perf_counter()
        rd = load_rd(BIG_FILE)
        self.done.emit((rd, time.perf_counter() - t0))


def pump(app, seconds):
    """让事件循环跑 seconds 秒（心跳靠它投递）。"""
    loop_start = time.perf_counter()
    while time.perf_counter() - loop_start < seconds:
        app.processEvents()          # 手动驱动事件循环
        time.sleep(0.005)


def test_stage3(app):
    """阶段3 写法：主线程里直接 load_rd → 预期卡死。"""
    hb = Heartbeat(app)
    hb.start()
    pump(app, 0.3)                    # 先攒几个正常心跳做基线
    print("  [阶段3] 主线程直接读文件…")
    t0 = time.perf_counter()
    load_rd(BIG_FILE)                 # ★ 就是这一句卡住主线程
    cost = time.perf_counter() - t0
    # 关键：读完后让事件循环转一下，那个「迟到的心跳」才会触发并被记下。
    # 它迟到的时间 ≈ 主线程被卡住的时长。
    pump(app, 0.3)
    hb.stop()
    print(f"  [阶段3] 读文件耗时 {cost:.2f}s，期间心跳最大延迟 {hb.max_lag_ms:.0f} ms")
    return cost, hb.max_lag_ms


def test_stage4(app):
    """阶段4 写法：丢给 QThread → 预期流畅。"""
    hb = Heartbeat(app)
    hb.start()
    pump(app, 0.3)
    print("  [阶段4] 后台线程读文件…")
    result = {}

    def on_done(payload):
        result["rd"], result["cost"] = payload

    worker = ReadWorker()
    worker.done.connect(on_done)
    worker.start()
    # 关键：这里主线程一直在 processEvents 响应心跳，不等待 worker
    while "cost" not in result:
        app.processEvents()
        time.sleep(0.005)
    hb.stop()
    print(f"  [阶段4] 读文件耗时 {result['cost']:.2f}s，期间心跳最大延迟 {hb.max_lag_ms:.0f} ms")
    return result["cost"], hb.max_lag_ms


def main():
    if not BIG_FILE.exists():
        print(f"找不到大文件 {BIG_FILE}，请先运行: .venv\\Scripts\\python.exe 04_thread\\make_slow_rd.py")
        sys.exit(1)
    app = QApplication(sys.argv)
    print(f"测试文件: {BIG_FILE.name} ({BIG_FILE.stat().st_size / 1e6:.0f} MB)\n")

    c3, lag3 = test_stage3(app)
    print()
    c4, lag4 = test_stage4(app)

    print("\n===== 结论 =====")
    print(f"  读文件耗时几乎一样（{c3:.2f}s vs {c4:.2f}s）——所以 QThread 不是让读文件变快。")
    print(f"  但主线程心跳延迟：阶段3 {lag3:.0f} ms  vs  阶段4 {lag4:.0f} ms")
    if lag3 > 1000 and lag4 < 300:
        print("  ✅ 验证通过：阶段3主线程被卡住近3秒；阶段4界面全程能响应。")
    else:
        print("  ⚠️ 数据不符合预期，检查文件大小或环境。")


if __name__ == "__main__":
    main()
