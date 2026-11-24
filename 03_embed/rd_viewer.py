# -*- coding: utf-8 -*-
"""阶段 3 · 图表嵌入：把 RD 谱画进 Qt 窗口，选文件即刷新。

这是本项目从「两个独立程序」变成「一个能用的软件」的关键一步。

运行（任意目录都行，脚本靠 __file__ 自己找项目根）：
  .venv\\Scripts\\python.exe 03_embed\\rd_viewer.py
  VS Code 点 ▶ 也行。
"""
import sys
from pathlib import Path

import numpy as np
import matplotlib
# K3.5: 后端必须在 import pyplot 之前定成 QtAgg，FigureCanvasQTAgg 才能嵌进 Qt。
# 不用 Agg（无界面），也不用默认的 tkagg（会另弹一个独立窗口）。
matplotlib.use("QtAgg")
import matplotlib.pyplot as plt

from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

# 阶段 1 的 rcParams 搬过来：中文不变方框、负号正常、刻度朝内（MATLAB 风）
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["xtick.direction"] = "in"
plt.rcParams["ytick.direction"] = "in"
plt.rcParams["font.size"] = 10

ROOT = Path(__file__).resolve().parent.parent
# 让脚本能 import 到 01_backend/rd_data.py（sys.path 加项目下的后端目录）
sys.path.insert(0, str(ROOT / "01_backend"))
from rd_data import load_rd  # noqa: E402  ★ 复用唯一数据入口，绘图/界面都不碰数据解析

# 绘图参数与阶段 1 完全一致，保证「接近 MATLAB」的风格连续
VMIN, VMAX = -50.0, 0.0
CMAP = "jet"


class RdViewer(QMainWindow):
    """主窗口：上方按钮栏 + 中间 Matplotlib 画布 + 底部状态栏。"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("RD 谱图上位机 · 阶段3")
        self.resize(900, 640)

        # ── K3.1 / K3.2: 造 Figure 和画布 ──────────────────────────
        # 用面向对象 API：fig 是一个独立对象，不经过 pyplot 的全局 gcf。
        # FigureCanvasQTAgg(fig) 把这张图包装成「一个能塞进布局的 QWidget」。
        self.fig = Figure(figsize=(7.2, 4.8), dpi=100)
        self.canvas = FigureCanvasQTAgg(self.fig)
        # canvas 要能随窗口伸缩：设 expanding，否则它保持固定像素尺寸
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # K3.3: 导航工具栏（复位/平移/缩放/保存）——阶段 1 弹窗自带的那排，这里手动挂上
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        # ── 控件 ────────────────────────────────────────────────
        self.open_btn = QPushButton("选择 RD 数据文件…")
        self.file_label = QLabel("还没有选择文件")

        # ── K3.4: 嵌套布局 ──────────────────────────────────────
        # 外层竖排：按钮行 → 工具栏 → 画布；按钮行内部横排：按钮 + 标签。
        central = QWidget()
        self.setCentralWidget(central)
        outer = QVBoxLayout(central)
        btn_row = QHBoxLayout()
        btn_row.addWidget(self.open_btn)
        btn_row.addWidget(self.file_label)
        outer.addLayout(btn_row)       # addLayout：把一行布局塞进竖布局
        outer.addWidget(self.toolbar)
        outer.addWidget(self.canvas)

        # ── K2.5 信号槽（阶段 2 已掌握，原样复用）──────────────────
        self.open_btn.clicked.connect(self.on_open_file)
        self.statusBar().showMessage("就绪")

        # 启动时画一次默认数据，打开窗口就能看到图（不用先点按钮）
        self._plot(ROOT / "data" / "fake_rd.npy", startup=True)

    def _plot(self, path, startup=False):
        """把某个文件画到画布上。★ 界面刷图的核心，就这几步。"""
        rd = load_rd(path)

        # K3.6: 关键——先把上一张图清干净再画。
        # colorbar 自己占一个 axes，不清的话每选一次文件就多一条色条，越叠越多。
        self.fig.clear()
        ax = self.fig.add_subplot(111)   # 一个子图占满整张 Figure

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

        # K3.7: ★ 界面的「刷新」就是这一句——把 Figure 的改动重绘到画布上。
        # 脚本里对应的是 fig.savefig()；这里不存盘，直接让控件重画。
        self.canvas.draw()

        if not startup:
            self.file_label.setText(Path(path).name)
            self.statusBar().showMessage(f"已显示: {path}")

    def on_open_file(self):
        """槽函数：弹选文件框 → 调 _plot 刷新 → 更新反馈。"""
        path, _ = QFileDialog.getOpenFileName(self, "选择 RD 数据", str(ROOT / "data"))
        if not path:
            self.statusBar().showMessage("已取消选择")
            return
        # K3.8: 用户可能选到非 .npy 文件，读失败不能让整个软件崩掉
        try:
            self._plot(path)
        except Exception as exc:
            self.statusBar().showMessage(f"读取失败: {exc}")
        else:
            self.file_label.setText(Path(path).name)
            self.statusBar().showMessage(f"已显示: {path}")


def main():
    app = QApplication(sys.argv)
    window = RdViewer()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
