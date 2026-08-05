# Ymir amd64 .deb build pipeline

Docker-based pipeline that builds the amd64 Debian packages for the Ymir toolchain:

- `gyc-<gcc-major>` — the GNU Ymir compiler (a GCC frontend), bundled with the Midgard standard
  library
- `gyllir` — the Ymir package manager

> This replaces the older Vagrant/VirtualBox-based workflow described in the repository root
> `README.md`, which no longer applies to this directory.

## Requirements

- Docker, with the daemon running and reachable by the `docker` Python SDK
- Network access to `gcc.gnu.org`, `github.com`, and the Ubuntu package mirrors (everything is
  cloned/downloaded during the build, there's no offline mode)
- Python 3.14+ ([uv](https://docs.astral.sh/uv/) is used to manage the environment; see
  `pyproject.toml` / `uv.lock`)

## Usage

```bash
uv run main.py config.yaml
```

`config.yaml` lists which ymir versions to build, e.g.:

```yaml
ymir_versions:
 - cxx_version
 - bootstrap_v0.1
# - bootstrap_v1.0
# - bootstrap_v1.1
# - bootstrap_v1.2
```

Comment/uncomment entries to control what gets built. Resulting `.deb` files are written to
`results/`.

### Build order matters

Ymir versions after `cxx_version` are bootstrapped from the previous version's compiler, so they
must be built in order: `cxx_version` → `bootstrap_v0.1` → `bootstrap_v1.0` → `bootstrap_v1.1` →
`bootstrap_v1.2`. Enabling a stage before its predecessor has produced a `.deb` in `results/` will
fail.

Each stage also builds `gyllir` against the `gyc` compiler it just produced.

### GCC target vs. compiler version

Each ymir version is associated with two GCC version numbers, which aren't always the same:

- the **target** GCC release the ymir frontend is merged into and built against (this is what
  ends up in the package name, e.g. `gyc-15_1.1.0_amd64.deb`)
- the **compiler** used to actually build that source tree

Older ymir releases (up to v1.0.0) target and are compiled with GCC 13.2.0. Starting with v1.1.0
the frontend targets GCC 15.2.0, though v1.1.0 itself is still compiled with the GCC 13.2.0
toolchain; from v1.2.0 onward both are GCC 15.2.0. This is a fixed compatibility property of each
release rather than something you configure — see `utils/builder.py` if a new version needs to be
added.

The Ubuntu base image follows the same split, because a newer Ubuntu's libraries can be too new to
build or run against an old GCC major: stages that compile the target's source tree use the Ubuntu
version matching the *compiler*, while the later packaging stages (which install the freshly built
`.deb`, itself `Depends: gcc-<target-major>`) use the Ubuntu version matching the *target*. In
practice, GCC 13.2.0 pairs with Ubuntu 24.04 and GCC 15.2.0 pairs with Ubuntu 26.04.

## Layout

- `main.py` — entry point, loads `config.yaml` and runs the builder
- `utils/builder.py` — orchestrates which versions get built and in what order
- `utils/cxx.py`, `utils/bootstrap.py`, `utils/gyllir.py` — one Docker-build wrapper class per
  build stage
- `jobs/clone_gcc/` — shared base image that bare-clones `gcc.git`
- `jobs/cxx_build/`, `jobs/bootstrap_build/` — build the ymir-enabled GCC compiler
- `jobs/gyllir_build/` — builds the `gyllir` package manager against an already-built compiler
- `results/` — output `.deb` files (gitignored)
