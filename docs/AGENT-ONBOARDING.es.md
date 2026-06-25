# AKASHA — onboarding para agentes de IA (ES)

**Frase del usuario (§3.1 AKASHA-TZ):**

> Configúrate según este proyecto de GitHub: `https://github.com/<user>/akash-brain`

Equivalente en ruso: «Настрой себя по данному проекту GitHub: `<URL>`»

Al recibir esta frase, **ejecuta todo el checklist abajo por tu cuenta**. El usuario no configura MCP, rules ni rutas manualmente.

---

## Checklist de bootstrap (orden obligatorio)

1. Detectar plataforma → `agent_id` (`cursor`, `claude-code`, `hermes`, `opencode`).
2. Instalar `akasha-core` si falta: `pip install git+https://github.com/sikuykus-lab/akasha-core.git`
3. `akash backend-detect` y `akash github-status`
4. `akash adopt <BRAIN_URL> --agent <agent_id>`
5. Leer en el brain: `skills/akash-bootstrap/SKILL.md`, `adapters/<agent_id>/bootstrap.md`, `inject.md`, hooks y MCP templates.
6. Instalar shell local (rules, hooks, MCP) **sin copiar** skills al proyecto.
7. Preguntar scope (`project` | `user`) → `akash configure ...`
8. `akash harvest --preview` → confirmación → `akash harvest` → `akash sync`
9. `akash pull` + `akash status`
10. Mensaje final §3.1: «Listo. Somos AKASHA.»

Contrato posterior: `pull` al inicio, `prepare` antes de tareas, `remember` + `sync` al final. No leer `skills/` enteros.

Ver checklist completo en `docs/AGENT-ONBOARDING.en.md`.
