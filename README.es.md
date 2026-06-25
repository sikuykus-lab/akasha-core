AKASHA Core (`akasha-core`)
===========================

Implementación en Python del núcleo de AKASHA (`akash-core v1`) según
`AKASHA-TZ v1.8`.

- Un único repositorio brain (GitHub privado o directorio en su servidor) con
  estructura fija.
- CLI `akash` y biblioteca `akash_core` para `adopt`, `pull`, `prepare`,
  `remember`, `sync`, etc.
- Backends `github` y `server` según el §2.5 de la especificación.

La especificación es la única fuente de verdad:

- `AKASHA-TZ v1.8` (copia en el repositorio de trabajo del usuario, p. ej.
  `Google Sheets/akash/AKASHA-TZ.md`).

## Estado legal / SaaS

`akasha-core` **no** es open source. Es un núcleo propietario de AKASHA.
Todos los derechos pertenecen a `sikuykus-lab`.

Uso permitido únicamente para:

- integrar con un repositorio brain privado de AKASHA (GitHub o servidor);
- soluciones SaaS compatibles con AKASHA aprobadas explícitamente por el propietario.

Textos de licencia:

- `LICENSE.md` — licencia principal (ruso, vinculante);
- `LICENSE.en.md` — traducción al inglés;
- `LICENSE.es.md` — traducción al español;
- `LICENSE.zh.md` — traducción al chino.

## Instalación (desde código fuente)

```bash
cd akasha-core
pip install -e .
```

## Inicio rápido

```bash
# bootstrap con un brain en GitHub
akash adopt https://github.com/user/akash-brain --agent cursor

# comprobar estado
akash status

# iniciar sesión
akash pull

# sync al final de la sesión
akash sync
```

Consulte el §11 de `AKASHA-TZ v1.8` y la documentación en
`docs/AKASHA-INSTRUCTIONS.*.md` para ver la lista completa de comandos
y el ciclo de vida.

