AKASHA Core (`akasha-core`)
===========================

这是按照 `AKASHA-TZ v1.8` 规范实现的 AKASHA 核心（`akash-core v1`）的
Python 版本。

- 单一 brain 仓库（GitHub 私有仓库或服务器目录），结构固定；
- CLI 工具 `akash` 与库 `akash_core`，用于 `adopt`、`pull`、`prepare`、
  `remember`、`sync` 等操作；
- 支持 `github` 与 `server` 两种 backend，详见规范 §2.5。

行为以规范为唯一依据：

- `AKASHA-TZ v1.8`（副本存放于用户的工作仓库，如
  `Google Sheets/akash/AKASHA-TZ.md`）。

## 法律 / SaaS 状态

`akasha-core` **不是** 开源项目，而是 AKASHA 的专有核心。
所有权利归 `sikuykus-lab` 所有。

仅允许以下使用场景：

- 与您的私有 AKASHA brain 仓库集成（GitHub 或自有服务器）；
- 经所有者明确批准的、与 AKASHA 兼容的 SaaS 解决方案。

许可证文本：

- `LICENSE.md` — 主许可证（俄文，为法律文本）；
- `LICENSE.en.md` — 英文翻译；
- `LICENSE.es.md` — 西班牙文翻译；
- `LICENSE.zh.md` — 中文翻译。

## 安装（从源码）

```bash
cd akasha-core
pip install -e .
```

## 快速开始

```bash
# 使用 GitHub 上的 brain 仓库进行 bootstrap
akash adopt https://github.com/user/akash-brain --agent cursor

# 查看状态
akash status

# 启动会话
akash pull

# 会话结束时同步
akash sync
```

完整命令列表与生命周期说明，请参考 `AKASHA-TZ v1.8` 的 §11 以及
`docs/AKASHA-INSTRUCTIONS.*.md` 中的文档。

