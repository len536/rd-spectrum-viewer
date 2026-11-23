# RD 谱图上位机软件 —— 研发过程仓库

> **任务来源**：张月荣老师《上位机软件设计》群通知（2026-11-23 09:53）
> **原始要求**：研制一个软件界面，根据计算生成的 RD（距离-多普勒）谱数据，绘图显示 RD 谱图；可用 Java 或 Python（本组选 **Python**）；图形展示风格尽可能接近 MATLAB 绘制的效果。
> **负责人**：冷（华东交通大学 · 计算机 2025 级 · 上位机软件开发分工）
> **这个仓库不只是代码**，是完整的研发过程记录 + 学习笔记，组会可以直接照着讲。

---

## 一、使用本仓库的规矩（先读这条）

> **跑通 ≠ 掌握。每个知识点都要能自己讲出来。**

1. 一个阶段一个 commit，commit 历史 = 研发时间线，可直接给老师看。
2. [`docs/00-知识点地图.md`](docs/00-知识点地图.md) 是**全部知识点的台账**，逐条打勾：`✅能讲清 / 🟡半懂 / ❌不懂`。
3. 每阶段结束做文档末尾的**自测题**，不看答案能答出来才算过。
4. 组会前看本页「当前进度 + 组会汇报要点」。

## 二、技术选型（组会必问，必须会讲）

| 层 | 选型 | 为什么（要能讲出来的理由） |
|---|---|---|
| 语言 | **Python 3.13**（系统自带，非 WorkBuddy 沙箱） | 老师给定 Python；科学计算生态成熟；最终能打包成 exe 交付 |
| 界面 | **PySide6**（阶段 2 启用） | Qt 官方 Python 绑定，**LGPL 许可**，闭源/交付无法律风险；PyQt5 是 GPL / 商业双许可，交付有隐患；两者 API 几乎一致，PyQt5 教程通用；且与后续 UAV 地面站项目技术栈统一 |
| 绘图 | **Matplotlib** + `FigureCanvasQTAgg` | 唯一能精细控制色表 / colorbar / 坐标轴、又能嵌进 Qt 窗口的成熟方案，最接近 MATLAB |
| 数据 | **NumPy**（视接口再加 SciPy） | RD 谱本质就是一个二维矩阵 |
| 打包 | **PyInstaller**（阶段 5） | 交付 .exe，老师电脑不用装 Python |

**几个"为什么不用"**（老师很可能追问）：
- 不用 PyQt5：许可证 + 非官方维护，见上表。
- 不用 Matplotlib 独立弹窗：要做的是**软件界面**，需要按钮、文件选择、布局，必须有 GUI 框架托管。
- 不一次装全套依赖：阶段 1 只需要 numpy + matplotlib（约 30MB），PySide6 约 150MB，等用到再装，出问题好定位。

## 三、研发路线（6 阶段，一步步来）

| 阶段 | 内容 | 状态 | commit |
|---|---|---|---|
| 0 | 立项：仓库骨架、环境、接口确认清单 | ✅ 2026-11-23 | 见 git log |
| 1 | 后端跑通：模拟 RD 数据 + MATLAB 风格出图 | ✅ 2026-11-23 | 见 git log |
| 2 | PySide6 主窗口 + 布局 + 信号与槽 | ⬜ 未开始 | |
| 3 | FigureCanvasQTAgg 图表嵌入 + 按钮触发 | ⬜ 未开始 | |
| 4 | 真实数据接入 + QThread 防界面卡死 | ⬜ 未开始 | |
| 5 | PyInstaller 打包 exe + 组会材料 | ⬜ 未开始 | |

> 顺序依据：**先后端、后前端**。先保证"数据能读、图能画对"，再套界面，出问题时能一眼定位是数据问题还是界面问题。

## 四、阶段 0-1 成果

![阶段1 出图效果](docs/images/rd_demo_stage1.png)

| 文件 | 作用 |
|---|---|
| `01_backend/make_fake_rd.py` | 造一份"像真的"模拟 RD 谱：噪声底 + 3 个动目标 + 零多普勒杂波带 |
| `01_backend/plot_rd_demo.py` | 读数据 → 画 MATLAB 风格伪彩图 → 保存 png |
| `docs/02-阶段1-学习笔记.md` | **逐行讲代码** + 每个知识点 + MATLAB 对照表 + 自测题答案 |

运行（先进入本仓库根目录）：
```bash
cd /d D:\WorkBuddyWorkspace\2026-11-23-12-10-51\rd-spectrum-viewer
.venv\Scripts\python.exe 01_backend\make_fake_rd.py
.venv\Scripts\python.exe 01_backend\plot_rd_demo.py
```
> `cd /d` 的 `/d` 是 CMD 专用：同时切**盘符**和目录。只写 `cd D:\xxx` 不会切到 D 盘，相对路径仍会在 C 盘找，报「系统找不到指定的路径」。PowerShell / Git Bash 不需要 `/d`。

💡 懒得切目录也行，**全绝对路径一步到位**（任何目录下都能跑，脚本靠 `__file__` 自己定位 `data/` 和 `docs/`）：
```bash
D:\WorkBuddyWorkspace\2026-11-23-12-10-51\rd-spectrum-viewer\.venv\Scripts\python.exe D:\WorkBuddyWorkspace\2026-11-23-12-10-51\rd-spectrum-viewer\01_backend\plot_rd_demo.py
```

## 五、环境搭建：掌握规则与从零复现

**规则**：环境分三档 —— 概念必须会讲（组会必问）、命令必须会复现（换电脑/现场演示）、网络排错不用练（本机噪音）。详见知识点地图 K0.1~K0.6。本次由 WorkBuddy 代装，**不要求删了重装**；**从阶段 2 起，新增依赖由负责人亲手敲命令**。

换一台 Windows 电脑，从零到出图只有四条命令（每条含义见知识点地图）：
```bash
py -3.13 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
.venv\Scripts\python.exe 01_backend\make_fake_rd.py
.venv\Scripts\python.exe 01_backend\plot_rd_demo.py
```

本机环境实测（2026-11-23）：Python 3.13 在 `C:\Users\ASUS\AppData\Local\Programs\Python\Python313`；git 2.55；GitHub **SSH 认证成功**、HTTPS 直连不通，故 push 走 `git@github.com:...`；无 `gh` CLI、无 token。

## 六、组会汇报要点（阶段 0-1）

1. **选型理由**：PySide6 / Matplotlib / NumPy 各自为什么（见第二节表格）。
2. **进展**：已跑通「数据 → 图」后端链路，界面按计划未开始。
3. **数据模型**：RD 谱 = 距离维 × 多普勒维的二维功率矩阵，颜色表示功率（dB）。
4. **风险控制**：数据接口尚未确定，已把读取逻辑收敛到 `load_rd()` **单一入口**，接口定了只改这一处，绘图与界面代码不动。
5. **下一步**：PySide6 主窗口 + 信号与槽。

## 七、待办 / 阻塞

- [ ] ⚠️ **找负责生成 RD 数据的同学确认接口** → 已备好可直接复制的提问清单：[`docs/01-接口确认清单.md`](docs/01-接口确认清单.md)
- [ ] 网页新建 GitHub 远程仓库并首次 push（本机无 gh CLI/token，需手动建一次；SSH 已配好）

## 八、目录约定

```
rd-spectrum-viewer/
├── README.md              项目总览 / 路线 / 开发日志 / 组会要点
├── requirements.txt       分阶段依赖（按阶段取消注释）
├── .gitignore
├── docs/
│   ├── 00-知识点地图.md     ★ 全部知识点台账 + 掌握标准 + 自测题
│   ├── 01-接口确认清单.md   ⚠️ 必须向数据同学确认的问题
│   ├── 02-阶段1-学习笔记.md 逐行讲解 + MATLAB 对照 + 答案
│   └── images/             出图成果（进仓库，组会直接展示）
├── 01_backend/            阶段1：纯脚本，无界面
├── data/                  运行时生成的模拟数据（gitignore，可随时重造）
└── .venv/                 虚拟环境（gitignore）
```
后续阶段的目录（如 `02_gui/`）随进度新建 —— **让仓库跟着项目一起长大**，这本身就是研发过程记录。
