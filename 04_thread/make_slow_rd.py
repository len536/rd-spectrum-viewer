# -*- coding: utf-8 -*-
"""造一个「大」RD 数据文件，专门用来肉眼验证 QThread 防卡死。

为什么用 .csv 不用 .npy？
  .npy 是二进制，读起来飞快，感觉不到卡；
  .csv 是文本，np.loadtxt 要一行行解析，几百万个数字要好几秒——
  正好让我们用肉眼看出「主线程被卡住」和「后台读、界面还能动」的区别。

运行：
  .venv\\Scripts\\python.exe 04_thread\\make_slow_rd.py

想让卡顿更明显 → 把 N 调大；想快点造完 → 把 N 调小。
"""
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "slow_rd.csv"

N = 4000          # 矩阵边长：N×N 个数字。默认 4000，读取约 2-3 秒，肉眼能看出卡顿
rng = np.random.default_rng(42)

print(f"正在造 {N}×{N} 的 csv（约 {N * N / 1e6:.1f} 百万个数字），稍等…")
t0 = time.perf_counter()
rd = rng.uniform(-45.0, -3.0, size=(N, N)).astype(np.float32)
np.savetxt(OUT, rd, delimiter=",", fmt="%.2f")
print(f"已生成: {OUT}")
print(f"  文件大小 {OUT.stat().st_size / 1e6:.1f} MB，造文件用时 {time.perf_counter() - t0:.1f} 秒")

# 实测读取耗时——这就是等下要在界面里「感受」的卡顿时长
t0 = time.perf_counter()
np.loadtxt(OUT, delimiter=",")
cost = time.perf_counter() - t0
print(f"  实测读取耗时: {cost:.1f} 秒  ← 记住这个数，等下对比用")
if cost < 1.0:
    print("  提示：读得太快，肉眼看不出卡顿。把上面的 N 调大到 2500 再跑一次。")
