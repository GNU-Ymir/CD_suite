#!/usr/bin/env python3

"""Verify the git refs utils/versions.py's STAGES matrix names actually exist
upstream, before a docker build gets far enough to fail on `git checkout`.

Only covers the GNU-Ymir GitHub repos (gymir, bootstrap, yruntime, Gyllir) — the
upstream GCC release branch is assumed to exist and is not checked here.
"""

import subprocess
import sys

from utils.versions import STAGES, BootstrapStage, CxxStage

GYMIR_REPO = "https://github.com/GNU-Ymir/gymir.git"
BOOTSTRAP_REPO = "https://github.com/GNU-Ymir/bootstrap.git"
YRUNTIME_REPO = "https://github.com/GNU-Ymir/yruntime.git"
GYLLIR_REPO = "https://github.com/GNU-Ymir/Gyllir.git"


def collect_refs() -> set[tuple[str, str]]:
    refs: set[tuple[str, str]] = set()
    for stage in STAGES.values():
        if isinstance(stage, CxxStage):
            # cxx.py hardcodes YMIR_VERSION="cxx" for both gymir and yruntime checkout.
            refs.add((GYMIR_REPO, "cxx"))
            refs.add((YRUNTIME_REPO, "cxx"))
        elif isinstance(stage, BootstrapStage):
            refs.add((GYMIR_REPO, stage.versions.ymir))
            refs.add((BOOTSTRAP_REPO, stage.versions.bootstrap))
            refs.add((YRUNTIME_REPO, stage.versions.midgard))

        # gyllir_version is the tag both jobs/gyllir_build and jobs/gyllir_self_build check
        # out of the Gyllir repo. prev_gyllir is not checked: it names an already-built .deb
        # in results/, not a ref to fetch.
        if stage.gyllir is not None:
            refs.add((GYLLIR_REPO, stage.gyllir.gyllir_version))
    return refs


def ref_exists(repo: str, ref: str) -> bool:
    result = subprocess.run(
        ["git", "ls-remote", "--exit-code", repo, ref],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result.returncode == 0


def main() -> int:
    refs = sorted(collect_refs())
    missing: list[tuple[str, str]] = []

    for repo, ref in refs:
        ok = ref_exists(repo, ref)
        print(f"{'OK  ' if ok else 'MISSING'} {repo} @ {ref}")
        if not ok:
            missing.append((repo, ref))

    if missing:
        print(f"\n{len(missing)}/{len(refs)} refs missing from upstream.")
        return 1

    print(f"\nAll {len(refs)} refs found upstream.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
