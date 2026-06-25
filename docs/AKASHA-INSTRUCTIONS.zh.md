AKASHA Core — 使用说明 (ZH)
============================

`akasha-core` 简要指南。**完整命令表**见 [README.zh.md](../README.zh.md)。

## 1. 前提

- Python 3.11+
- `git`；GitHub 需 `gh auth login` 或 SSH
- 安装：

```bash
python3 -m pip install --user git+https://github.com/sikuykus-lab/akasha-core.git
```

## 2. Bootstrap（推荐）

聊天触发语：

> **按此 GitHub 项目配置：** `https://github.com/sikuykus-lab/akasha-core`

终端：

```bash
python3 -m akash_core.cli onboard https://github.com/sikuykus-lab/akasha-core --agent cursor
```

完成后：`~/.akash/config.local`，brain 克隆于 `~/.akash/github/<user>/akash-brain`。

智能体清单：`docs/AGENT-ONBOARDING.zh.md`。

## 3. 已有 brain

```bash
akash adopt https://github.com/<user>/akash-brain --agent cursor
```

## 4. 服务器 brain

```bash
akash adopt --server user@host:~/.akash/brain --agent hermes
```

## 5. 生命周期

```bash
akash pull
akash prepare "任务描述"
akash read-skill <skill_id>
akash remember "事实"
akash record-outcome <skill_id> success
akash sync
```

## 6. 诊断

```bash
akash doctor
akash status
akash install-shell   # 核心升级后
```
