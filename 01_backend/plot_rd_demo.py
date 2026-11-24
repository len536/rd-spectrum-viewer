# -*- coding: utf-8 -*-
"""
阶段 1 · 用 Matplotlib 画出"接近 MATLAB"的 RD 谱图

MATLAB 里的等价写法：
    imagesc(rd); colormap(jet); colorbar; axis xy;
    xlabel('Doppler bin'); ylabel('Range bin'); caxis([-50 0]);
本文件就是它的 Python 逐句翻译（完整对照表见 docs/02-阶段1-学习笔记.md）。

运行：
  .venv\\Scripts\\python.exe 01_backend\\plot_rd_demo.py
输出：
  docs/images/rd_demo_stage1.png
"""
from pathlib import Path
import sys
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

# ★ 阶段 3 起，数据入口抽到独立模块 rd_data.py，脚本与界面共用同一份。
# 脚本方式运行时，脚本所在目录（01_backend）在 sys.path 里，直接 import 即可。
from rd_data import load_rd

# ============ ① 全局样式：一次设置，整张图生效（相当于 MATLAB 的 set(groot,...)）============
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]  # 中文不变方框
plt.rcParams["axes.unicode_minus"] = False      # 负号不变成小方块
plt.rcParams["xtick.direction"] = "in"          # 刻度朝内，MATLAB 默认风格
plt.rcParams["ytick.direction"] = "in"
plt.rcParams["font.size"] = 11

# ============ ② 显示参数 ============
VMIN, VMAX = -50.0, 0.0     # 显示动态范围（dB）：超出部分颜色"饱和"，不再细分
CMAP = "jet"                  # 老 MATLAB 默认色表 → 满足"接近 MATLAB"的要求
DPI_SAVE = 300                # 保存图片的清晰度（组会 PPT 用）

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "fake_rd.npy"
OUT_PNG = ROOT / "docs" / "images" / "rd_demo_stage1.png"


# load_rd 已移到 01_backend/rd_data.py（阶段 3），本脚本从那里 import。
# 知识点 K1.17「单一入口」不变：现在脚本和 Qt 界面 import 的是同一个函数。

def plot_rd(rd, out_png=OUT_PNG, cmap=CMAP, vmin=VMIN, vmax=VMAX):
    """把二维矩阵画成 MATLAB 风格伪彩图。★ 这个函数以后会被 Qt 界面原样复用。"""
    # ③ 面向对象写法：fig = 整张画布，ax = 坐标系。
    #    嵌 Qt 时用的是 fig（FigureCanvasQTAgg(fig)），所以从现在起就不用 pyplot 全局状态
    fig, ax = plt.subplots(figsize=(8.2, 5.2), dpi=110)

    # ④ imshow：把矩阵每个元素当成一个"色块"画出来
    im = ax.imshow(
        rd,                       # shape=(距离门, 多普勒) → 第 0 轴自动落在 y 轴，正好 y=距离
        cmap=cmap,                # 数值 → 颜色的映射表
        vmin=vmin, vmax=vmax,     # 颜色条两端对应的数值（显示门限）
        origin="lower",           # 第 0 行画在下方，等价于 MATLAB 的 axis xy
        aspect="auto",            # 两维量纲不同，不强制格子为正方形，让图铺满
        interpolation="nearest",  # 不做插值模糊，保留"每个距离门/通道"的格子感
    )

    # ⑤ colorbar：颜色和数值的对照尺，MATLAB 风格必须有
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    cbar.set_label("功率 / dB")
    cbar.ax.tick_params(direction="in")

    # ⑥ 坐标轴：现在用 bin 索引；拿到标定向量后可改成
    #    extent=[d_min, d_max, r_min, r_max] 直接显示 m、m/s
    ax.set_xlabel("多普勒通道 / Doppler bin")
    ax.set_ylabel("距离门 / Range bin")
    ax.set_title("RD 谱（距离-多普勒）· 阶段1 模拟数据")
    ax.set_xticks(np.arange(0, rd.shape[1] + 1, 8))
    ax.set_yticks(np.arange(0, rd.shape[0] + 1, 16))

    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=DPI_SAVE, bbox_inches="tight")   # ⑦ 必须先存
    if matplotlib.get_backend().lower() != "agg":              # Agg 是无界面后端，不弹窗
        plt.show()                                             # 再弹窗（show 之后 figure 可能被释放）
    plt.close(fig)
    print(f"图已保存 -> {out_png}")
    return fig


def main():
    rd = load_rd(DATA_FILE)
    plot_rd(rd)


if __name__ == "__main__":
    main()
