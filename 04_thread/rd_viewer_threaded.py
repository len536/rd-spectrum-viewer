# -*- coding: utf-8 -*-
"""阶段 4 · 多格式接入 + QThread 防卡死。

相对阶段 3 的三处升级：
  ① 数据入口 load_rd() 已支持 .npy/.csv/.txt/.mat（在 rd_data.py 里，界面不用改）
  ② 读文件丢到 QThread 工作线程，主线程不卡（本文件的 LoadWorker）
  ③ 换电脑没默认数据时现场造一份，不再 FileNotFoundError

运行：
  .venv\\Scripts\\python.exe 04_thread\\rd_viewer_threaded.py
"""
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("QtAgg")                       # 必须在 import pyplot 之前
import matplotlib.pyplot as plt

from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from PySide6.QtCore import QThread, Signal    # ★ 阶段4新词：QThread 线程 / Signal 信号
from PySide6.QtWidgets import (
    QApplication, QFileDialog, QHBoxLayout, QLabel,
    QMainWindow, QPushButton, QSizePolicy, QVBoxLayout, QWidget,
)

# 中文/刻度样式（沿用阶段 1，保证 MATLAB 风格连续）
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["xtick.direction"] = "in"
plt.rcParams["ytick.direction"] = "in"
plt.rcParams["font.size"] = 10

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "01_backend"))
from rd_data import load_rd                   # noqa: E402  唯一数据入口
from make_fake_rd import make_fake_rd         # noqa: E402  默认数据兜底用

VMIN, VMAX = -50.0, 0.0
CMAP = "jet"
DEFAULT_DATA = ROOT / "data" / "fake_rd.npy"


class LoadWorker(QThread):
    """在后台线程读文件。★ QThread 不是让读文件变快，是让界面不卡。

    两个信号（Signal）用来跟主线程通信：
      loaded = 读成功，参数带上读好的二维数组
      failed = 读失败，参数带上错误文字
    """
    loaded = Signal(object)     # object = 可以传任何对象，这里传 numpy 数组
    failed = Signal(str)        # str = 错误提示文字

    def __init__(self, path):
        super().__init__()
        self.path = path

    def run(self):
        """线程真正干的活——只做读数据，绝不碰界面控件。"""
        try:
            rd = load_rd(self.path)
        except Exception as exc:
            self.failed.emit(str(exc))        # 出错：把错误文字送回主线程
        else:
            self.loaded.emit(rd)              # 成功：把数组送回主线程
            # ★ 注意：这里不能直接 self.canvas / self.label —— 工作线程不许碰 UI


class RdViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RD 谱图上位机 · 阶段4（多格式 + 防卡死）")
        self.resize(900, 640)
        self.worker = None                    # 保存当前工作线程引用，防止被回收

        self.fig = Figure(figsize=(7.2, 4.8), dpi=100)
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        self.open_btn = QPushButton("选择 RD 数据文件…")
        self.file_label = QLabel("还没有选择文件")

        central = QWidget()
        self.setCentralWidget(central)
        outer = QVBoxLayout(central)
        btn_row = QHBoxLayout()
        btn_row.addWidget(self.open_btn)
        btn_row.addWidget(self.file_label)
        outer.addLayout(btn_row)
        outer.addWidget(self.toolbar)
        outer.addWidget(self.canvas)

        self.open_btn.clicked.connect(self.on_open_file)
        self.statusBar().showMessage("就绪")

        # 启动时画默认数据；没有就现场造一份（修阶段 3 的技术债）
        self._startup_plot()

    def _ensure_default_data(self):
        """换电脑 clone 后 data/ 是空的 → 现场造一份，保证软件打开就能用。"""
        if not DEFAULT_DATA.exists():
            DEFAULT_DATA.parent.mkdir(parents=True, exist_ok=True)
            np.save(DEFAULT_DATA, make_fake_rd())
            self.statusBar().showMessage("默认数据缺失，已自动生成")
        return DEFAULT_DATA

    def _startup_plot(self):
        path = self._ensure_default_data()
        self._draw(load_rd(path))             # 启动时数据量小，直接画即可

    def _draw(self, rd):
        """把二维数组画到画布上（只管画，不管读——读是 load_rd 的事）。"""
        self.fig.clear()                      # 清掉上一张，防 colorbar 叠加
        ax = self.fig.add_subplot(111)
        im = ax.imshow(
            rd, cmap=CMAP, vmin=VMIN, vmax=VMAX,
            origin="lower", aspect="auto", interpolation="nearest",
        )
        cbar = self.fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
        cbar.set_label("功率 / dB")
        cbar.ax.tick_params(direction="in")
        ax.set_xlabel("多普勒通道 / Doppler bin")
        ax.set_ylabel("距离门 / Range bin")
        ax.set_title("RD 谱（距离-多普勒）")
        ax.set_xticks(np.arange(0, rd.shape[1] + 1, 8))
        ax.set_yticks(np.arange(0, rd.shape[0] + 1, 16))
        self.fig.tight_layout()
        self.canvas.draw()                    # 界面的「刷新」就是这句

    # ── 阶段 4 新增：信号槽连工作线程 ──────────────────────────
    def on_open_file(self):
        """点按钮：弹选文件框 → 启动后台线程去读（不在这里直接读！）。"""
        path, _ = QFileDialog.getOpenFileName(self, "选择 RD 数据", str(ROOT / "data"))
        if not path:
            self.statusBar().showMessage("已取消选择")
            return
        self.open_btn.setEnabled(False)       # 读文件中禁用按钮，防连点
        self.statusBar().showMessage("正在读取（后台）…")
        self.worker = LoadWorker(path)        # 造工作线程
        self.worker.loaded.connect(self._on_loaded)   # 成功 → 主线程画图
        self.worker.failed.connect(self._on_failed)   # 失败 → 主线程提示
        self.worker.finished.connect(self._on_finished)  # 无论如何 → 恢复按钮
        self.worker.start()                   # 启动线程；run() 在后台执行

    def _on_loaded(self, rd):
        """槽函数：收到后台送来的数组，在主线程里画图（碰 UI 是安全的）。"""
        self._draw(rd)
        self.file_label.setText(self.worker.path.name)
        self.statusBar().showMessage(f"已显示: {self.worker.path}")

    def _on_failed(self, msg):
        """槽函数：收到错误信息，只在状态栏提示，不崩窗口。"""
        self.statusBar().showMessage(f"读取失败: {msg}")

    def _on_finished(self):
        """线程干完（成功或失败）都会发 finished，这里恢复按钮。"""
        self.open_btn.setEnabled(True)


def main():
    app = QApplication(sys.argv)
    window = RdViewer()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
