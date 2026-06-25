AKASHA Core — Instrucciones (ES)
================================

Este documento explica cómo conectar y utilizar AKASHA Core (`akasha-core`)
de acuerdo con `AKASHA-TZ v1.8`.

1. Requisitos previos
---------------------

- Python 3.11+ instalado.
- `git` instalado y autenticación en GitHub configurada (para backend GitHub).
- Paquete instalado:

```bash
pip install git+https://github.com/sikuykus-lab/akasha-core.git
```

2. Opción A — brain en un repositorio privado de GitHub
-------------------------------------------------------

1. Cree o elija un repositorio **privado** para el brain de AKASHA, por ejemplo:

   - `https://github.com/<user>/akash-brain`

2. En la máquina/agente donde esté instalado `akasha-core`, ejecute el bootstrap:

   - En la terminal:

     ```bash
     akash adopt https://github.com/<user>/akash-brain --agent cursor
     ```

   - O dígale a su agente de código (Cursor, Claude Code, etc.):

     > Configúrate según este proyecto de GitHub: `https://github.com/<user>/akash-brain`

3. Después del bootstrap:

   - `~/.akash/config.local` contiene `backend: github` y `brain_url`.
   - El clon local del brain se guarda en `~/.akash/github/<owner>/<repo>`.

3. Opción B — brain en su propio servidor
-----------------------------------------

1. En el servidor, cree un directorio para el brain, por ejemplo:

   - `~/.akash/brain`

2. Si el agente ya se ejecuta **en** el servidor (Hermes por SSH, etc.):

   - Ejecute:

     ```bash
     akash adopt --server user@host:~/.akash/brain --agent hermes
     ```

   - O en el chat:

     > Usa mi servidor en lugar de GitHub para el cerebro de AKASHA — `ssh user@host`, brain en `~/.akash/brain`

3. Para un brain remoto vía SSH:

   - En `~/.akash/config.local` verá `backend: server`, `brain_host` y `brain_path`.

4. Comandos principales del CLI
-------------------------------

Todos los comandos se describen en el §11 de `AKASHA-TZ v1.8`. Resumen:

- `akash backend-detect` — detectar backends disponibles (`github` / `server`).
- `akash init` — inicializar la estructura del brain en el directorio actual.
- `akash migrate` — migrar un brain existente al diseño actual.
- `akash configure` — editar manualmente `~/.akash/config.local` (backend, brain_url/brain_host, scope).
- `akash pull` — inicio de sesión: `pull` del brain + carga de la memoria caliente (`persona`, `rapport`, `ACTIONS`).
- `akash prepare "descripción de la tarea"` — crear un pack de skills para una nueva tarea.
- `akash read-skill <skill_id>` — leer `SKILL.md` del pack actual.
- `akash remember "hecho"` — registrar un hecho en el buffer de sesión.
- `akash record-outcome <skill_id> <success|failure> [--help-score N]` — registrar el resultado del uso del skill.
- `akash compact-check` — comprobar si es necesario compactar la memoria caliente.
- `akash sync` — `pull → compact → NAV → push` del brain.
- `akash harvest [--preview] [--merge]` — ejecutar el harvest según los adaptadores.
- `akash import-legacy` — modo reducido de harvest para SOUL/USER/MEMORY/AGENTS.
- `akash export-session` / `akash export-pack` / `akash ingest-session` — transporte UPP para agentes sin tools.
- `akash status` — mostrar `brain_version`, backend e información básica.

5. Ciclo de vida típico de una sesión
-------------------------------------

1. El agente inicia un nuevo chat → el hook de ciclo de vida ejecuta:

   ```bash
   akash pull
   ```

2. Para una nueva tarea, el agente ejecuta:

   ```bash
   akash prepare "descripción de la tarea"
   akash read-skill <skill_id>   # según necesidad
   ```

3. Durante el trabajo:

   ```bash
   akash remember "hecho sobre el usuario/tarea"
   akash record-outcome <skill_id> success --help-score 1
   ```

4. Periódicamente y al final de la sesión:

   ```bash
   akash sync
   ```

