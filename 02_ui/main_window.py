"""阶段 2 · 主窗口骨架：最小可跑的 PySide6 程序。

规矩（阶段 1 收口时定死）：
  本文件只给骨架 + TODO，关键逻辑由负责人亲手填。
  跑通不算掌握，能讲出每一行「为什么」才算。

运行（任意目录下都行，脚本按 __file__ 自己找项目根）：
  .venv\\Scripts\\python.exe 02_ui\\main_window.py
  VS Code 点 ▶ 也行，解释器已用 .vscode/settings.json 固定。

验收：弹窗 + 点按钮能弹出选文件框 + 选完标签和状态栏都变。
"""
import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

ROOT = Path(__file__).resolve().parent.parent


class MainWindow(QMainWindow):
    """主窗口：标题 + 中央控件（标签、按钮）+ 底部状态栏。"""

    def __init__(self):
        super().__init__()  # K2.2: 先建好 Qt 父类内部状态，后面所有 setXxx 才有意义
        self.setWindowTitle("RD 谱图上位机 · 阶段2")
        self.resize(420, 180)

        # K2.2: QMainWindow 必须有且只有一个中央控件，布局要挂在它上面
        central = QWidget()
        self.setCentralWidget(central)

        # K2.4: 控件先造出来；「摆在哪」是 TODO 1 的事
        self.label = QLabel("还没有选择文件")
        self.button = QPushButton("选择 RD 数据文件…")

        # ── TODO 1（K2.3 布局，K2.7 父子对象）────────────────
        # 目标：让 label 在上、button 在下，窗口拉伸时跟着变。
        # 提示：
        #   layout = QVBoxLayout(central)   # 括号里传 central = 直接认父（K2.7）
        #   layout.addWidget(self.label)
        #   layout.addWidget(self.button)
        # 为什么不用 self.label.move(x, y)？见笔记 2.3 节。
        # ───────────────────────────────────────────────────
        pass  # ← 删掉这行，写你的代码

        # ── TODO 2（K2.5 信号与槽）───────────────────────────
        # 目标：按钮被点 → 自动调用 self.on_open_file。
        # 提示：self.button.clicked.______(self.on_open_file)
        # 坑：括号里传的是「函数本身」，不要写 ()！
        #     写 connect(self.on_open_file()) 会在连接那一刻就执行，且连了个 None。
        # ───────────────────────────────────────────────────
        pass  # ← 删掉这行，写你的代码

        # K2.2: 状态栏是 QMainWindow 自带的，一句话取出来用
        self.statusBar().showMessage("就绪")

    # ── TODO 3（K2.4 QFileDialog，K2.6 槽函数）────────────────
    # 目标：点按钮后做三件事：
    #   ① QFileDialog.getOpenFileName(...) 弹出系统选文件框
    #      它返回 (路径字符串, 过滤器字符串) 两个值，用两个变量接
    #   ② 路径非空时 self.label.setText(...) 显示它
    #      （只想显示文件名可用 Path(路径).name）
    #   ③ self.statusBar().showMessage(...) 给一句反馈
    # 提示：getOpenFileName 的第一个参数是父窗口 self，第二个是对话框标题。
    # ──────────────────────────────────────────────────────
    def on_open_file(self):
        pass  # ← 删掉这行，写你的代码


def main():
    # K2.1: 每个 Qt 程序必须先造一个 QApplication，且只能有一个
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()  # 不 show() 窗口不会出现在屏幕上
    sys.exit(app.exec())  # K2.1: 进入事件循环；关窗后 exec() 才返回，sys.exit 拿返回值退出


if __name__ == "__main__":
    main()
