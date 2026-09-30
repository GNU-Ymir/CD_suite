# CLAUDE.md

This file provides guidance to Claude Code when working with code in this directory
(`amd64/deb`). See also `../../CLAUDE.md` for repo-wide conventions (Linear issue tracking).

## What this is

Docker-based build pipeline that produces the `.deb` packages for the Ymir toolchain on amd64:
- `gyc-<major>` — the GNU Ymir compiler (a GCC frontend, from the `gymir` repo)
- `gyllir` — the Ymir package manager
- the Midgard standard library, bundled into the `gyc` package

It replaced an older Vagrant/VirtualBox-based workflow (see git history around
"change: change vagrant to docker"); the root `README.md` still documents that old workflow and is
stale for this directory.

## Entry point

```bash
uv run main.py config.yaml
```

`main.py` just reads the given YAML config and hands it to `utils/builder.py`'s `Builder`, which
loops over `ymir_versions` and dispatches to the right builder class. Output `.deb` files land in
`results/`.

## The version chain

Each ymir release depends on the previous one being already built, because later compilers are
bootstrapped with earlier ones:

```
cxx_version -> bootstrap_v0.1 (0.1.0) -> bootstrap_v1.0 (1.0.0) -> bootstrap_v1.1 (1.1.0) -> bootstrap_v1.1.1 (1.1.1)
```

`config.yaml`'s `ymir_versions` list controls which stages actually run (commented-out entries are
skipped). Enable a stage only once everything it depends on already has a `.deb` sitting in
`results/`, or the docker build will fail trying to `COPY`/`shutil.copy` a file that doesn't exist.

`utils/versions.py`'s `STAGES` dict is the global version matrix: one `CxxStage`/`BootstrapStage`
entry per `ymir_versions` key, holding which GCC/Ubuntu versions and previous-stage dependencies
that stage builds with — see "Version knobs per stage" below. `utils/builder.py`'s `Builder.run()`
just looks a stage up in `STAGES` and dispatches to the right builder class; it has no version
knowledge of its own. There is no per-run config for the matrix itself; it reflects a fixed
compatibility fact about each ymir release, not something meant to be tuned per invocation.

- `utils.cxx.CxxBuilder` — builds the `cxx_version` stage from scratch (clones bare `gcc.git`,
  merges in the `gymir` frontend, compiles). This is the only stage with no previous `.deb`
  dependency.
- `utils.bootstrap.VxxBuilder` — builds every `bootstrap_vX.Y` stage. Installs the *previous*
  stage's `gyc.deb`/`gyllir.deb` as the ymir compiler, then compiles the new frontend/runtime
  version against it.
- `utils.gyllir.GyllirBuilder` — builds `gyllir` against a given already-built `gyc.deb`. Runs
  after every stage above.

## Version knobs per stage — don't conflate them

`utils/versions.py`'s `GycVersions` dataclass bundles the independent version numbers a
`bootstrap_vX.Y` stage needs, all plumbed through `VxxBuilder` as Docker build args for
`bootstrap_build/Dockerfile`:

- **`target`** (`GCC_VERSION` / `GCC_MAJOR_VERSION`) — which upstream GCC release ref (branch
  `releases/gcc-N` or a specific point-release tag like `releases/gcc-N.M.P`) the ymir frontend
  source gets merged into and built against. Drives the deb package name
  (`gyc-<major>_<ymir_version>_amd64.deb`), install paths under
  `/usr/libexec/gcc/x86_64-linux-gnu/<major>/`, and the `Depends: gcc-<major>` line in
  `control.in`. `GycVersions.target_major` derives the bare major from it.
- **`compiler`** (`COMPILER_MAJOR_VERSION`) — the *host* toolchain (`gcc-N`/`g++-N`, installed via
  apt) actually invoked to compile that source tree (`CC=gcc-N CXX=g++-N ../gcc-src/configure`).
  This can differ from the target — e.g. a given ymir version's frontend source may only build
  cleanly with an older host compiler even though it targets a newer GCC release branch.
- **`ymir`** (`YMIR_VERSION`) — the `gymir` frontend (binding plugin) git tag checked out into
  `gcc-src/gcc/ymir`, and the version label used for the produced `gyc` package/filename.
- **`bootstrap`** (`GYC_VERSION`) — the `GNU-Ymir/bootstrap` repo's git tag, checked out separately
  in the `fetch_gcc_version` stage. Can diverge from `ymir` if a bootstrap-shim fix needs to trail
  or lead the frontend tag.
- **`midgard`** (`MIDGARD_VERSION`) — the `yruntime`/`midgard` stdlib's git tag, checked out in the
  `build_midgard` stage. `MIDGARD_SHORT_VERSION` (its value with the patch component stripped)
  namespaces the installed `include/ymir/<short>` path and the `libgymidgard-*` library filenames.
- **`bootstrap_midgard`** (`YMIR_BOOTSTRAP_MIDGARD_VERSION`, optional) — the `yruntime` tag whose
  runtime `ymir1` itself links: the std the bootstrap source pins in its `gyllir.toml`, named by
  gymir's own `YMIR_VERSION` from 1.7.0 on (`Make-lang.in` links `-lgymidgard-debug_<short>` of
  it). Not the midgard the stage ships (`midgard`), nor necessarily the one the previous
  `gyc.deb` bundles: gyc 1.6.0 ships midgard 1.8 while bootstrap 1.7.0 pins 1.9. When set,
  `fetch_gcc_version` builds that tag's debug archive with the previous gyc/gyllir and installs it
  as `/usr/lib/libgymidgard-debug_<short>.a` (upstream downloads it from the yruntime release
  instead), and `make` is handed the same value. Leave `None` when the previous `gyc.deb` already
  carries it or the tag predates it (up to 1.5.x `ymir1` links the archive gyllir builds in
  `bootstrap/.deps/std`; 1.6.0 links `-lgymidgard-debug_1.6`, bundled by gyc 1.5.3). A gymir tag
  whose `YMIR_VERSION` names it fails fast in `fetch_gcc_version` if the stage leaves it unset.

`VxxBuilder` also takes a single **`ubuntu_version`** (`UBUNTU_VERSION`, plus `CLONE_IMAGE` for the
shared clone base) reused for *both* the `fetch_gcc_version`/`configure`/`make` stages (which
actually need the ubuntu matching the **compiler**) and the `build_midgard` stage (which installs
the just-built `.deb`, `Depends: gcc-<target-major>`, so it actually needs the ubuntu matching the
**target**). This only cleanly works when `compiler` and `target` share a major (or at least an
ubuntu release) — see the `bootstrap_v1.1` gotcha below for the one stage where that's not true.
`GyllirBuilder` is unaffected by this collapse: it's a separate builder with its own
`ubuntu_version`, always picked to match the **target** major of the `gyc.deb` it installs.

Current known-good pairings (the `STAGES` matrix in `utils/versions.py`):

| ymir version | target gcc | compiler gcc | `VxxBuilder` ubuntu | `GyllirBuilder` ubuntu |
|---|---|---|---|---|
| cxx | 13 | 13 | — (no VxxBuilder) | 24.04 |
| v0.1.0 | 13 | 13 | 24.04 | 24.04 |
| v1.0.0 | 13 | 13 | 24.04 | 24.04 |
| v1.1.0 | 15 | 13 | 24.04 (compiler's) | 26.04 (target's) |
| v1.1.1 | 15 | 15 | 26.04 | 26.04 |

`v1.1.0` is the one stage where target and compiler diverge; `bootstrap_v1.1.1` exists to converge
back onto a single gcc-15 compiler for everything downstream (see Linear `YMI-49`).

Because target majors can change between stages (e.g. v1.0.0 -> v1.1.0, 13 -> 15), `VxxBuilder`
takes explicit `prev_gyc`/`prev_gyllir` identifier strings (e.g. `"15_1.1.0"`, matching the
previous stage's actual output filename `gyc-15_1.1.0_amd64.deb`) rather than deriving them from
the current stage's own target — it must not assume the previous artifact shares this stage's
target major.

If you add a new `bootstrap_vX.Y` stage, add one `BootstrapStage` entry to the `STAGES` dict in
`utils/versions.py` (`Builder.run()` itself needs no changes). You need: the five required
`GycVersions` fields (plus `bootstrap_midgard` if the gymir tag's `YMIR_VERSION` names a
`YMIR_BOOTSTRAP_MIDGARD_VERSION` the previous `gyc.deb` does not bundle), the shared
`ubuntu_version` for `VxxBuilder`, the `prev_gyc`/`prev_gyllir` identifiers for the previous
stage's output, and (if built) a `GyllirSpec` with its own `compile_with`/
`ubuntu_version` (target major and its matching ubuntu). Leave `gyllir` unset when no new Gyllir
release goes with the stage (e.g. `bootstrap_v1.6.0` through `bootstrap_v1.8.0` all keep using the
gyllir 1.8.0 built by `bootstrap_v1.5.3`) — `prev_gyllir` then keeps naming that older build.

## Gotchas

- `results/` is not cleaned between runs and old artifacts keep whatever major-version filename
  they were built with. If you change which target GCC major a stage uses, stale files from a
  previous config (e.g. `gyc-15_0.1.0_amd64.deb` from back when everything targeted 15) will not
  match what the next stage now looks for (`gyc-13_0.1.0_amd64.deb`) — rebuild the affected stages
  rather than assuming old `results/` output is still valid.
- `jobs/clone_gcc/Dockerfile` builds a base image that every other job's Dockerfile `FROM`'s via
  the `CLONE_IMAGE` build arg. It only bare-clones `gcc.git` on top of a given
  `ubuntu:${UBUNTU_VERSION}`; the actual release branch and host/target compiler packages are
  installed per-job in `cxx_build`/`bootstrap_build`. Because the Ubuntu version is baked into the
  image at build time (unlike the compiler, which is just an apt package layered on after), there
  are effectively two cached variants in play, tagged `gyc:gcc_clone_<ubuntu_version>` (e.g.
  `gyc:gcc_clone_24.04`, `gyc:gcc_clone_26.04`). Both `CxxBuilder` and `VxxBuilder` call
  `createCloneImage()` every run to make sure the variant they need exists; Docker's build cache
  makes repeat calls for an already-built variant cheap.
- The `apt-get install gcc-N g++-N` steps assume that major version's package is still available
  in the Ubuntu release actually in use for that stage. Older majors (e.g. gcc-13) can disappear
  from a distro's repos over time, which is part of why the Ubuntu base is pinned per-major rather
  than always using the newest release.
- Both `cxx_build/Dockerfile` and `bootstrap_build/Dockerfile` patch the cloned `gymir` source
  right after checkout, inserting a `Make-lang.in` dependency line
  (`ymir/gycspec.o: $(CORETYPES_H) $(PLUGIN_HEADERS) $(INSN_ATTR_H)`) under the `CFLAGS-ymir` line
  if it's missing. This works around a missing build dependency in some upstream `gymir` tags; the
  `grep -qF ... || sed -i ...` guard keeps it idempotent if a future tag already has the line.
- `bootstrap_build/Dockerfile`'s `build_midgard` stage has two build paths, picked by whether the
  checked-out `yruntime` carries a `gyllir.toml`. Up to midgard 1.3.0 it is a CMake project
  (`cmake .. && make install DESTDIR=`); from 1.3.1 on, CMake is gone and it is built by
  `gyllir build <target>` from a manifest, then installed by yruntime's own `install` script. Only
  the three library targets that `install` picks up are built — `gyllir build` with no target would
  also build the `midgard_tests` executable, whose link needs an already-installed midgard that the
  freshly built gyc does not carry (upstream's own Dockerfile survives this because its gyc comes
  from a released .deb that still bundles the previous midgard). That script
  writes to the real `/usr`, so the stage runs it and mirrors the result into the package root.
  The gyllir it runs is the *previous* stage's (the same `gyllir.deb` already copied in for
  `fetch_gcc_version`), not the `GYLLIR_VERSION` the yruntime tag names — the chain has only
  built what it has built. Requires `cpio`, which `install` uses to copy the `.yr` sources.
- The `MIDGARD_SHORT_VERSION` that suffixes the installed archives (`libgymidgard-debug_<short>.a`)
  and namespaces the include dir comes from a different file in each era, and the stage reads
  whichever one the build system in use reads: CMake names them after `YMIR_BOOTSTRAP_VERSION` in
  the yruntime checkout's `YMIR_VERSION` (the gyc it is built *with*), while `install` names them
  after the midgard release itself — its `VERSION` file up to 1.9.0, and from 1.10.0 on (where
  `VERSION` is gone) `gyllir.toml`'s top-level `version`, read through
  `.github/scripts/midgard-version.sh`, which the stage calls too when present. These disagree as
  soon as a bootstrap trails a midgard release — midgard 1.5.0 carries `YMIR_BOOTSTRAP_VERSION=1.4.0`, so
  the old rule would have suffixed it `1.4` while `gyc` links `-lgymidgard-debug_1.5`. The stage
  asserts the derived value matches the major.minor of the stage's own `midgard` knob, which is
  what `Make-lang.in` bakes into `gycspec.o` as `LIBYMIDGARD_VERSION`.
- Every `apt-get update` lives in the same `RUN` as the installs it feeds. Split across two `RUN`s
  it becomes a cached layer holding an index that still names exact `.deb` versions long after
  Ubuntu has dropped them from the pool, and the install then dies on a wall of 404s for files that
  no longer exist — a failure that looks like a network problem but is really a stale cache. The
  cost is that touching one of these lines re-runs everything after it, including `clone_gcc`'s
  bare `gcc.git` clone.
- Building requires a working Docker daemon and network access to `gcc.gnu.org`, `github.com`, and
  the Ubuntu apt mirrors; there's no offline/vendored mode.
- `bootstrap_v1.1`'s single `ubuntu_version` is set to the *compiler's* ubuntu (24.04, since
  `compiler=13` there), because `fetch_gcc_version`/`configure`/`make` need it. That means
  `build_midgard` in that same stage runs `apt-get install gcc-15 g++-15` on ubuntu 24.04, which
  may not carry a `gcc-15` package — this stage may need re-splitting into two ubuntu values (or
  dropping in favor of `bootstrap_v1.1.1`, which avoids the problem entirely by compiling with
  gcc-15 throughout) if it's ever re-enabled.
