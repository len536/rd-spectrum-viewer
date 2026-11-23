# -*- coding: utf-8 -*-
"""
阶段 1 · 造一份"像真的"RD（距离-多普勒）谱模拟数据

为什么先造假数据？
  真实 RD 数据由负责算法的同学提供，接口还没定（见 docs/01-接口确认清单.md）。
  但绘图代码不能干等 —— 先造一份结构一样的假数据，把"读 → 画"链路跑通，
  等真数据到了，只换 load_rd() 一个函数即可。

运行：
  .venv\\Scripts\\python.exe 01_backend\\make_fake_rd.py
输出：
  data/fake_rd.npy   二进制，画图脚本读这个
  data/fake_rd.csv   文本，仅用来演示"另一种格式长什么样"
"""
from pathlib import Path
import numpy as np

# ============ 可调参数：改这里，再跑一次，看图怎么变（最快的理解方式）============
N_RANGE = 128        # 距离门数量 → 矩阵"行数"（第 0 轴）
N_DOPPLER = 64       # 多普勒通道数 → 矩阵"列数"（第 1 轴）
SEED = 20261123      # 随机种子：固定它，每次生成完全一样，汇报截图才不会变
NOISE_FLOOR_DB = -45.0   # 噪声底（dB）：整张图的"背景亮度"
NOISE_STD_DB = 2.0       # 噪声起伏（dB）

# 三个动目标：(距离门, 多普勒通道, 峰值dB, 距离展宽, 多普勒展宽)
# 峰值 dB 是"比 0dB 低多少"，-3 表示很强、-9 表示较弱
TARGETS = [
    (30,  16, -3.0, 2.0, 1.5),
    (72,  46, -6.0, 2.5, 2.0),
    (105, 26, -9.0, 1.8, 1.2),
]

# 零多普勒杂波：静止地物在"零速度"那一列形成一条亮带
CLUTTER_PEAK_DB = -8.0
CLUTTER_WIDTH = 2.2

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"


def make_fake_rd():
    """返回 shape=(N_RANGE, N_DOPPLER) 的功率矩阵，单位 dB。"""
    rng = np.random.default_rng(SEED)          # 固定种子 → 可复现

    # ① 噪声底：整张图先铺一层"沙沙"的背景
    rd = rng.normal(NOISE_FLOOR_DB, NOISE_STD_DB, (N_RANGE, N_DOPPLER))

    # ② 坐标网格：把两个一维坐标"摊"成两个二维矩阵，后面才能对整个矩阵一次性运算
    #    d_grid[i,j] = j（多普勒/列索引），r_grid[i,j] = i（距离/行索引）
    #    indexing="xy" 保证返回形状是 (N_RANGE, N_DOPPLER)，和 rd 对得上
    d_grid, r_grid = np.meshgrid(
        np.arange(N_DOPPLER), np.arange(N_RANGE), indexing="xy"
    )

    # ③ 三个动目标：用二维高斯"亮斑"近似点目标经过 FFT 后的主瓣
    for r0, d0, peak, sr, sd in TARGETS:
        shape = np.exp(-(((d_grid - d0) ** 2) / (2 * sd ** 2)
                         + ((r_grid - r0) ** 2) / (2 * sr ** 2)))
        contrast = peak - NOISE_FLOOR_DB        # 目标比噪声底高多少 dB
        # 用 maximum 而不是 += ：亮的盖住背景、暗处不扰动噪声，
        # 才符合"该处功率被目标主导"的物理情形
        rd = np.maximum(rd, NOISE_FLOOR_DB + contrast * shape)

    # ④ 零多普勒杂波：零速在多普勒中心列（fftshift 之后）
    d_zero = N_DOPPLER // 2
    clutter_shape = np.exp(-((d_grid - d_zero) ** 2) / (2 * CLUTTER_WIDTH ** 2))
    clutter_contrast = CLUTTER_PEAK_DB - NOISE_FLOOR_DB
    rd = np.maximum(rd, NOISE_FLOOR_DB + clutter_contrast * clutter_shape)

    return rd.astype(np.float32)               # float32 够用，省一半内存


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    rd = make_fake_rd()

    np.save(DATA_DIR / "fake_rd.npy", rd)                                  # 二进制，保 dtype，最快
    np.savetxt(DATA_DIR / "fake_rd.csv", rd, delimiter=",", fmt="%.3f")  # 文本，通用但大

    print(f"shape = {rd.shape}   (行=距离门 {rd.shape[0]}, 列=多普勒通道 {rd.shape[1]})")
    print(f"dtype = {rd.dtype}")
    print(f"功率范围: {rd.min():.2f} dB ~ {rd.max():.2f} dB")
    print(f"零多普勒中心列: 第 {N_DOPPLER // 2} 列")
    print(f"已保存 -> {DATA_DIR / 'fake_rd.npy'}")
    print(f"已保存 -> {DATA_DIR / 'fake_rd.csv'} (仅用于演示文本格式)")


if __name__ == "__main__":
    main()
