AKASHA Core — 使用说明 (ZH)
===========================

本文件简要说明如何按照 `AKASHA-TZ v1.8` 使用 AKASHA Core (`akasha-core`)。

1. 前置条件
-----------

- 已安装 Python 3.11 及以上版本；
- 已安装 `git`，如使用 GitHub 作为 brain 后端，则需配置好 GitHub 认证；
- 已安装 `akasha-core` 包：

```bash
pip install git+https://github.com/sikuykus-lab/akasha-core.git
```

2. 方案 A：brain 存储在 GitHub 私有仓库
---------------------------------------

1. 创建或选择一个 **私有** AKASHA brain 仓库，例如：

   - `https://github.com/<user>/akash-brain`

2. 在安装了 `akasha-core` 的机器/代理上执行 bootstrap：

   - 在终端中：

     ```bash
     akash adopt https://github.com/<user>/akash-brain --agent cursor
     ```

   - 或在代码代理（Cursor、Claude Code 等）中直接发送：

     > 根据此 GitHub 项目完成自我配置：`https://github.com/<user>/akash-brain`

3. bootstrap 完成后：

   - `~/.akash/config.local` 中记录 `backend: github` 和 `brain_url`；
   - brain 仓库的本地克隆位于 `~/.akash/github/<owner>/<repo>`。

3. 方案 B：brain 存储在自有服务器
---------------------------------

1. 在服务器上为 brain 创建目录，例如：

   - `~/.akash/brain`

2. 如果代理 **运行在** 该服务器上（例如通过 SSH 登录的 Hermes）：

   - 在服务器上执行：

     ```bash
     akash adopt --server user@host:~/.akash/brain --agent hermes
     ```

   - 或在聊天中发送：

     > 使用我的服务器代替 GitHub 存储 AKASHA 的大脑 — `ssh user@host`，brain 目录为 `~/.akash/brain`

3. 如通过 SSH 使用远程 brain：

   - `~/.akash/config.local` 中将包含 `backend: server`、`brain_host` 和 `brain_path`。

4. 核心 CLI 命令
----------------

所有命令在 `AKASHA-TZ v1.8` 的 §11 中有完整说明。这里给出简要列表：

- `akash backend-detect` — 检测可用后端（`github` / `server`）；
- `akash init` — 在当前目录中初始化 brain 仓库结构；
- `akash migrate` — 将已有 brain 迁移到当前结构；
- `akash configure` — 手动编辑 `~/.akash/config.local`（backend、brain_url/brain_host、scope 等）；
- `akash pull` — 会话开始：`pull` brain + 读取 hot memory（`persona`、`rapport`、`ACTIONS`）；
- `akash prepare "任务描述"` — 为新任务生成 skill pack；
- `akash read-skill <skill_id>` — 从当前 pack 中读取 `SKILL.md`；
- `akash remember "事实"` — 将事实写入会话缓冲区；
- `akash record-outcome <skill_id> <success|failure> [--help-score N]` — 记录 skill 使用结果；
- `akash compact-check` — 检查 hot memory 是否需要压缩；
- `akash sync` — `pull → compact → NAV → push` brain；
- `akash harvest [--preview] [--merge]` — 基于适配器执行 harvest；
- `akash import-legacy` — 针对 SOUL/USER/MEMORY/AGENTS 的简化 harvest 模式；
- `akash export-session` / `akash export-pack` / `akash ingest-session` — 用于无 tools 代理的 UPP 传输；
- `akash status` — 显示当前 `brain_version`、backend 及基本信息。

5. 典型会话生命周期
-------------------

1. 代理中新建会话（聊天） → 生命周期 hook 调用：

   ```bash
   akash pull
   ```

2. 有新任务时，代理调用：

   ```bash
   akash prepare "任务描述"
   akash read-skill <skill_id>   # 按需调用
   ```

3. 处理任务过程中：

   ```bash
   akash remember "关于用户/任务的事实"
   akash record-outcome <skill_id> success --help-score 1
   ```

4. 会话中定期以及结束时：

   ```bash
   akash sync
   ```

