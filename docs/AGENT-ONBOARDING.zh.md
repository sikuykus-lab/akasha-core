# AKASHA — AI 代理 onboarding（ZH）

**用户触发语（§3.1 AKASHA-TZ）：**

> 根据此 GitHub 项目完成自我配置：`https://github.com/<user>/akash-brain`

俄语等价句：«Настрой себя по данному проекту GitHub: `<URL>`»

收到此句后，**请自行完成下方全部步骤**。用户无需手动配置 MCP、rules 或路径。

---

## Bootstrap 检查清单（必须按顺序）

1. 识别平台 → `agent_id`（`cursor`、`claude-code`、`hermes`、`opencode` 等）
2. 若无 `akash` 命令：`pip install git+https://github.com/sikuykus-lab/akasha-core.git`
3. 运行 `akash backend-detect` 与 `akash github-status`
4. 运行 `akash adopt <BRAIN_URL> --agent <agent_id>`
5. 在 brain 仓库中阅读：`skills/akash-bootstrap/SKILL.md`、`adapters/<agent_id>/` 下各模板文件
6. 安装本地适配器外壳（rules、hooks、MCP），**不要**将 skills 复制到工作项目
7. 询问 scope（`project` | `user`）→ `akash configure ...`
8. `akash harvest --preview` → 用户确认 → `akash harvest` → `akash sync`
9. `akash pull` + `akash status`
10. 向用户发送 §3.1 最终消息：「就绪。我们是 AKASHA。」

后续契约：会话开始 `pull`，新任务 `prepare`，结束 `sync`。禁止通读整个 `skills/` 目录。

完整步骤见 `docs/AGENT-ONBOARDING.en.md`。
