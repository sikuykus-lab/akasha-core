AKASHA Core (`akasha-core`)
===========================

**AKASHA** 的 Python 核心 — 为 AI 智能体（Cursor、Claude Code、Hermes 等）提供共享记忆与 skills。

- 单一 **brain**（GitHub 私有仓库或服务器目录）— persona、rapport、skills、NAV。
- CLI `akash` 与库 `akash_core`。
- 后端：`github` 或 `server`。
- 在聊天中 **一句话** onboard — 智能体自动安装核心并创建您的私有 `akash-brain`。

**语言：** [Русский](README.md) · [English](README.en.md)

## 聊天触发语

已配置 GitHub（`gh auth login` 或 SSH）时：

> **按此 GitHub 项目配置：** `https://github.com/sikuykus-lab/akasha-core`

智能体按 `docs/AGENT-ONBOARDING.zh.md` 执行 bootstrap。另见 `docs/AGENT-ONBOARDING.ru.md`、`docs/AGENT-ONBOARDING.en.md`。

## 安装

```bash
python3 -m pip install --user git+https://github.com/sikuykus-lab/akasha-core.git
```

从源码（开发）：

```bash
cd akasha-core && pip install -e .
```

## 快速开始

```bash
# 完整 bootstrap：SaaS → 私有 brain → hooks → harvest
python3 -m akash_core.cli onboard https://github.com/sikuykus-lab/akasha-core --agent cursor

# 已有 brain
akash adopt https://github.com/<your-user>/akash-brain --agent cursor

# 服务器上的 brain
akash adopt --server user@host:~/.akash/brain --agent hermes

akash status
akash pull
akash sync
```

## CLI 命令

| 命令 | 说明 |
|------|------|
| `akash onboard [url]` | 完整 bootstrap：安装 → brain → shell → harvest → sync |
| `akash adopt <url>` | 连接已有 brain（GitHub URL） |
| `akash adopt --server <user@host:path>` | 用户服务器上的 brain |
| `akash create-brain` | 在 GitHub 创建私有 `akash-brain` |
| `akash install-shell` | 升级后重装 Cursor hooks 与 rule |
| `akash doctor` | 诊断 CLI、配置、brain、GitHub |
| `akash ensure-cli` | 若未安装则安装 `akasha-core` |
| `akash backend-detect` | 可用后端：`github` / `server` |
| `akash github-status` | GitHub 认证状态 |
| `akash init` | 在当前目录 scaffold brain |
| `akash migrate` | 迁移 brain 至最新结构 |
| `akash configure` | 编辑 `~/.akash/config.local` |
| `akash pull [--steal]` | 会话开始 + **brain 锁**（单 writer） |
| `akash session-status` | 锁持有者、TTL |
| `akash prepare "任务"` | 为任务编织 skill pack |
| `akash read-skill <id>` | 从当前 pack 读取 SKILL.md |
| `akash remember "事实"` | 会话缓冲记录事实 |
| `akash record-outcome <id> success\|failure` | 记录 skill 使用结果 → usage.jsonl |
| `akash compact-check` | 检查热记忆是否需压缩 |
| `akash sync` | pull → compact → NAV → push 至 brain |
| `akash harvest [--preview] [--merge]` | 从智能体收割至 brain |
| `akash import-legacy` | 窄收割：SOUL/USER/MEMORY/AGENTS |
| `akash export-session --agent <id>` | UPP：可粘贴到聊天的记忆块 |
| `akash export-pack "任务" --agent <id>` | UPP：任务 pack |
| `akash ingest-session --agent <id>` | UPP：解析 AKASHA-INGEST 块 |
| `akash status` | brain_version、backend、scope |

MCP 工具（若启用）与上述操作一一对应。

## 并行智能体

同一时间只有 **一个会话** 可写入 brain：

1. **本机** — `~/.akash/locks/` 文件锁（同一 Mac 上多个 Cursor 聊天）。
2. **跨机器** — brain 内 `state/session_lock.json`（`pull` 时 push）。

第二个智能体在 `pull` / `sync` / `harvest` 时会失败。锁僵死：TTL 过后（10 分钟，`prepare` / `remember` 续期）使用 `akash pull --steal`。

## 会话生命周期

```
sessionStart  →  akash pull
新任务        →  akash prepare "…"  →  akash read-skill <id>
工作中        →  akash remember  ·  akash record-outcome
结束          →  akash sync
```

仅通过 `prepare` / `read-skill` 读取 skills，勿整目录扫描 `skills/`。

## 法律声明

`akasha-core` 为 **专有** 软件，非开源。权利归属：`sikuykus-lab`。

允许：与 **您的** 私有 brain 集成；经所有者批准的 AKASHA 兼容 SaaS。

- [LICENSE.md](LICENSE.md) — 俄文（具法律效力）
- [LICENSE.en.md](LICENSE.en.md) · [LICENSE.zh.md](LICENSE.zh.md) — 译文

用户说明：`docs/AKASHA-INSTRUCTIONS.zh.md`（同目录含 ru/en）。
