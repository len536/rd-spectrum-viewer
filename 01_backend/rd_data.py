# -*- coding: utf-8 -*-
"""RD 谱数据入口（唯一）——阶段 4 升级为「按扩展名自动识别多种格式」。

为什么独立成模块（组会可讲）：
  阶段 1 时 load_rd() 写在 plot_rd_demo.py 里。阶段 3 界面要复用它，
  若直接 `from plot_rd_demo import load_rd`，会把那个脚本的 pyplot / rcParams
  等绘图副作用一起 import 进来。把纯数据逻辑单独放这里，脚本和界面都从
  同一个地方 import，既保持「单一入口」，又不带绘图副作用。

接口契约（对调用方的承诺，永远不变）：
  输入：一个数据文件路径
  输出：shape=(距离门, 多普勒通道) 的二维 float 数组，单位 dB
  ★ 阶段 4 升级：现在按文件后缀自动选读取方式（.npy / .csv / .txt / .mat）。
    真实数据接口确认后，只改对应的 _load_xxx 分支即可，调用方不动。
"""
from pathlib import Path

import numpy as np

# 接口清单第 3 问还没回：数据是线性功率 / dB / 复数 IQ？
# 当前假设已是 dB。真数据若不是，在这里做转换（见 to_db 的说明）。
DEFAULT_UNIT = "db"          # "db" / "power"（线性功率）/ "iq"（复数）
TRANSPOSE = False            # 接口清单第 2 问：两维若反了，改这里为 True


def _load_text(path):
    """读 .csv / .txt：每行一个距离门，用逗号（或空白）分隔。"""
    # loadtxt = load + text：把文本表格读成二维数组
    # delimiter="," 告诉它列与列之间用什么隔开；csv 是逗号
    return np.loadtxt(path, delimiter=",")


def _load_npy(path):
    """读 .npy：NumPy 专用二进制，最快、保留 dtype。"""
    return np.load(path)


def _load_mat(path):
    """读 MATLAB .mat：读出来是字典，按里面的变量名取值。"""
    # scipy 不是阶段 1-3 的依赖，所以到这里才 import（用到才装）。
    # 没装时给一句人话提示，而不是甩一个 ModuleNotFoundError 给界面。
    try:
        from scipy.io import loadmat
    except ImportError:
        raise RuntimeError(
            "读取 .mat 需要 scipy，请先安装：\n"
            ".venv\\Scripts\\python.exe -m pip install scipy -i https://pypi.tuna.tsinghua.edu.cn/simple"
        )
    data = loadmat(path)                 # 字典：键是 MATLAB 里的变量名
    # 下划线的键（__header__ 等）是 MATLAB 元数据，不是数据，跳掉
    keys = [k for k in data.keys() if not k.startswith("__")]
    if len(keys) != 1:
        raise ValueError(f".mat 里有多个变量 {keys}，请确认哪个是 RD 矩阵（变量名要问数据同学）")
    return data[keys[0]]


def to_db(rd, unit):
    """按数据的实际单位转成 dB——接口清单第 3 问的落点。

    dB = 10*log10(功率)。线性功率能差几十万倍，取对数压到 -50~0 才好上色。
    """
    if unit == "db":
        return rd
    if unit == "power":
        return 10 * np.log10(rd + 1e-12)      # +1e-12 防止 log10(0) 变 -inf
    if unit == "iq":
        iq = np.abs(rd) ** 2                  # 复数 I/Q → 功率 = |幅度|²
        return 10 * np.log10(iq + 1e-12)
    raise ValueError(f"未知单位 {unit}，只支持 db / power / iq")


def load_rd(path):
    """读一个 RD 谱文件 → 返回二维数组（dB）。全项目唯一的数据入口。"""
    path = Path(path)
    suffix = path.suffix.lower()              # 后缀小写：.NPY 也认得

    # 按后缀分派到不同的读取函数——新增格式只在这里加一个分支
    if suffix == ".npy":
        rd = _load_npy(path)
    elif suffix in (".csv", ".txt"):
        rd = _load_text(path)
    elif suffix == ".mat":
        rd = _load_mat(path)
    else:
        raise ValueError(f"暂不支持格式 {suffix}，支持 .npy / .csv / .txt / .mat")

    rd = to_db(rd, DEFAULT_UNIT)              # 统一转成 dB
    if TRANSPOSE:
        rd = rd.T                             # 两维反了就转置（接口确认后定）

    # ★ 快速自检：必须是二维矩阵，否则后面 imshow 会出怪图
    if rd.ndim != 2:
        raise ValueError(f"RD 谱必须是二维矩阵，实际 {rd.ndim} 维，shape={rd.shape}")
    print(f"[load_rd] {path.name} shape={rd.shape}, dtype={rd.dtype}, "
          f"范围 {rd.min():.1f} ~ {rd.max():.1f} dB")
    return rd
