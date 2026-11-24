# -*- coding: utf-8 -*-
"""RD 谱数据入口（唯一）——阶段 3 从绘图脚本中独立出来。

为什么独立成模块（组会可讲）：
  阶段 1 时 load_rd() 写在 plot_rd_demo.py 里。阶段 3 界面要复用它，
  若直接 `from plot_rd_demo import load_rd`，会把那个脚本的 pyplot / rcParams
  等绘图副作用一起 import 进来。把纯数据逻辑单独放这里，脚本和界面都从
  同一个地方 import，既保持「单一入口」，又不带绘图副作用。

接口契约（对调用方的承诺，永远不变）：
  输入：一个数据文件路径
  输出：shape=(距离门, 多普勒通道) 的二维 float 数组，单位 dB
  真实数据来了（.txt/.csv/.mat/Socket）只改这个函数内部，调用方不动。
"""
import numpy as np


def load_rd(path):
    """读一个 RD 谱文件 → 返回二维数组（dB）。这是全项目唯一的数据入口。"""
    rd = np.load(path)
    if rd.ndim != 2:
        raise ValueError(f"RD 谱必须是二维矩阵，实际 {rd.ndim} 维，shape={rd.shape}")
    print(f"[load_rd] shape={rd.shape}, dtype={rd.dtype}, "
          f"范围 {rd.min():.1f} ~ {rd.max():.1f} dB")
    return rd
