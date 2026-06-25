# Bootstrap Cursor + AKASHA (§3.1–§3.2)

- [ ] `gh auth login` (если ещё не)
- [ ] `python3 -m pip install --user git+https://github.com/sikuykus-lab/akasha-core.git`
- [ ] `python3 -m akash_core.cli onboard https://github.com/sikuykus-lab/akasha-core --agent cursor --scope project|user`
- [ ] Проверка: `python3 -m akash_core.cli doctor`
- [ ] Финальное сообщение §3.1

`onboard` создаёт `.cursor/rules/akasha-lifecycle.mdc` и `.cursor/hooks.json` с `python3 -m akash_core.cli` (PATH не нужен).
