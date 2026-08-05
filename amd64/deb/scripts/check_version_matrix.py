#!/usr/bin/env python3

"""Static sanity checks over utils/versions.py and config.yaml.

Runs no docker, touches no network: it only checks that the STAGES matrix is
internally consistent (a prev_gyc/prev_gyllir a stage names actually matches
what some earlier stage would produce) and that config.yaml only selects
stages that exist. See CLAUDE.md's "results/ is not cleaned between runs"
gotcha for the failure mode this catches ahead of a wasted docker build.
"""

import sys

import yaml

from utils.versions import STAGES, BootstrapStage, CxxStage


def produced_identifiers(name: str, stage: CxxStage | BootstrapStage) -> tuple[str, str | None]:
    """The (gyc, gyllir) identifiers a stage's builder writes into results/.

    Mirrors utils/cxx.py's and utils/bootstrap.py's retreiveDebFile naming.
    """
    if isinstance(stage, CxxStage):
        gyc_id = f"{stage.target}_cxx"
    else:
        gyc_id = f"{stage.versions.target_major}_{stage.versions.bootstrap}"

    gyllir_id = stage.gyllir.gyllir_version if stage.gyllir is not None else None
    return gyc_id, gyllir_id


def main() -> int:
    errors: list[str] = []

    gyc_ids: dict[str, str] = {}
    gyllir_ids: dict[str, str] = {}
    for name, stage in STAGES.items():
        gyc_id, gyllir_id = produced_identifiers(name, stage)
        gyc_ids[gyc_id] = name
        if gyllir_id is not None:
            gyllir_ids[gyllir_id] = name

    for name, stage in STAGES.items():
        if not isinstance(stage, BootstrapStage):
            continue
        if stage.prev_gyc not in gyc_ids:
            errors.append(
                f"{name}: prev_gyc={stage.prev_gyc!r} does not match any stage's "
                f"produced gyc identifier ({sorted(gyc_ids)})"
            )
        if stage.prev_gyllir not in gyllir_ids:
            errors.append(
                f"{name}: prev_gyllir={stage.prev_gyllir!r} does not match any stage's "
                f"produced gyllir identifier ({sorted(gyllir_ids)})"
            )

    with open("config.yaml") as f:
        cfg = yaml.safe_load(f)

    for v in cfg["ymir_versions"]:
        if v not in STAGES:
            errors.append(f"config.yaml: ymir_versions entry {v!r} is not a key in STAGES")

    if errors:
        print("Version matrix sanity check failed:")
        for err in errors:
            print(f"- {err}")
        return 1

    print(f"Version matrix OK: {len(STAGES)} stages, config.yaml selects {len(cfg['ymir_versions'])}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
