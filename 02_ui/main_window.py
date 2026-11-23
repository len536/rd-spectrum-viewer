"""阶段 2 · 主窗口：最小可跑的 PySide6 窗口程序。

对照 docs/03-阶段2-学习笔记.md 看逐段讲解。
能讲出每一行「为什么」才算掌握——跑通只是第一步。

运行（任意目录下都行，脚本按 __file__ 自己找项目根）：
  .venv\\Scripts\\python.exe 02_ui\\main_window.py
  VS Code 点 ▶ 也行。

功能：点按钮 → 弹系统选文件框 → 选中后标签显示文件名、状态栏给反馈。
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

        # K2.4: 控件先造出来；「摆在哪」由下面的布局决定
        self.label = QLabel("还没有选择文件")
        self.button = QPushButton("选择 RD 数据文件…")

        # K2.3 + K2.7: 竖布局把标签、按钮依次挂到中央控件上。
        # QVBoxLayout(central) 的 central 就是「认父」，父子同生共死（K2.7）。
        # 用布局而非 move(x, y)：窗口缩放时控件自动重排，不用钉死坐标。
        layout = QVBoxLayout(central)
        layout.addWidget(self.label)
        layout.addWidget(self.button)

        # K2.5: 把按钮的 clicked 信号连到 on_open_file 槽函数。
        # 注意传的是函数本身 on_open_file，不是 on_open_file()——后者会立刻执行。
        self.button.clicked.connect(self.on_open_file)

        # K2.2: 状态栏是 QMainWindow 自带的一句话取出来用
        self.statusBar().showMessage("就绪")

    # K2.4 + K2.6: 槽函数——按钮被点时由事件循环自动调用。
    def on_open_file(self):
        # ① 弹系统选文件框，返回 (路径, 过滤器) 两个值；第二个用不上，用 _ 接住丢弃。
        path, _ = QFileDialog.getOpenFileName(self, "选择 RD 数据")

        # ② 用户点「取消」时 path 是空字符串 ""，直接给个反馈并返回。
        if not path:
            self.statusBar().showMessage("已取消选择")
            return

        # ③ 真选了文件：标签只显示文件名（Path(path).name = 去掉目录只剩最后一段），
        #    状态栏显示完整路径。f"..." 是 f-string，把 {path} 换成变量的值。
        self.label.setText(Path(path).name)
        self.statusBar().showMessage(f"已选择: {path}")


def main():
    # K2.1: 每个 Qt 程序必须先造一个 QApplication，且只能有一个
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()  # 不 show() 窗口不会出现在屏幕上
    sys.exit(app.exec())  # K2.1: 进事件循环；关窗后 exec() 才返回，sys.exit 拿返回值退出


if __name__ == "__main__":
    main()
