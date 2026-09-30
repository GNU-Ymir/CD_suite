#!/usr/bin/env python3

from dataclasses import dataclass


@dataclass(frozen=True)
class GycVersions:
    """The independent version knobs that go into compiling one gyc stage.

    - compiler: host gcc-N/g++-N (apt package) actually invoked to compile the tree.
    - target: upstream GCC release ref the ymir frontend is merged into/targets
      (may be a full point release like "15.2.1" or a bare major like "15").
    - ymir: gymir frontend (binding plugin) git tag, also used as the produced
      package's version label.
    - bootstrap: GNU-Ymir/bootstrap repo git tag.
    - midgard: yruntime/midgard stdlib git tag bundled into the produced gyc.
    - bootstrap_midgard: yruntime/midgard git tag whose runtime ymir1 is linked against - the std
      the bootstrap (ymirc) source pins in its gyllir.toml, named YMIR_BOOTSTRAP_MIDGARD_VERSION
      in gymir's own YMIR_VERSION from gymir 1.7.0 on. Built from source with the previous
      stage's gyc when the previous gyc.deb does not already carry it. None for earlier tags,
      which link either the archive gyllir builds next to libymirc.a or the midgard the previous
      gyc.deb bundles.
    """
    compiler: str
    target: str
    ymir: str
    bootstrap: str
    midgard: str
    bootstrap_midgard: str | None = None

    @property
    def compiler_major(self) -> str:
        return self.compiler.split(".")[0]

    @property
    def target_major(self) -> str:
        return self.target.split(".")[0]


@dataclass(frozen=True)
class GyllirSpec:
    """Args for the GyllirBuilder that follows a stage's gyc build.

    prev_gyllir: set from gyllir 1.2.0 onward, where Gyllir builds itself (utils.gyllir.
    GyllirSelfBuilder, jobs/gyllir_self_build) instead of using CMake (utils.gyllir.GyllirBuilder,
    jobs/gyllir_build) - the identifier (e.g. "1.1.0") of the already-built gyllir .deb in
    results/ used to compile this one. Leave None for the CMake-built versions before 1.2.0.
    """
    gyc: str
    compile_with: str
    gyllir_version: str
    ubuntu_version: str
    prev_gyllir: str | None = None


@dataclass(frozen=True)
class CxxStage:
    """The from-scratch cxx_version stage (utils.cxx.CxxBuilder)."""
    target: str
    compiler: str
    ubuntu_version: str
    gyllir: GyllirSpec | None = None


@dataclass(frozen=True)
class BootstrapStage:
    """A bootstrap_vX.Y stage (utils.bootstrap.VxxBuilder), built on a previous gyc/gyllir."""
    prev_gyc: str
    prev_gyllir: str
    versions: GycVersions
    ubuntu_version: str
    gyllir: GyllirSpec | None = None


# Ubuntu base image is picked per GCC major: 13.x needs ubuntu 24.04 (ubuntu 26.04's libs are
# too new to build/run gcc-13 against), 15.x uses ubuntu 26.04.
UBUNTU_FOR_GCC13 = "24.04"
UBUNTU_FOR_GCC15 = "26.04"

# The global version matrix: one entry per ymir_versions key config.yaml can select, in dependency
# order. Enable a stage in config.yaml only once everything it depends on already has a .deb
# sitting in results/ (see CLAUDE.md's "The version chain").
STAGES: dict[str, CxxStage | BootstrapStage] = {
    "cxx_version": CxxStage (
        # target gcc-13, compiled with gcc-13, both on ubuntu 24.04
        target="13",
        compiler="13",
        ubuntu_version=UBUNTU_FOR_GCC13,
        gyllir=GyllirSpec (gyc="13_cxx", compile_with="13", gyllir_version="cxx", ubuntu_version=UBUNTU_FOR_GCC13),
    ),
    "bootstrap_v0.1": BootstrapStage (
        # target gcc-13, compiled with gcc-13, both on ubuntu 24.04
        prev_gyc="13_cxx",
        prev_gyllir="cxx",
        versions=GycVersions (compiler="13", target="13", ymir="0.1.0", bootstrap="0.1.0", midgard="0.1.0"),
        ubuntu_version=UBUNTU_FOR_GCC13,
        gyllir=GyllirSpec (gyc="13_0.1.0", compile_with="13", gyllir_version="0.1.0", ubuntu_version=UBUNTU_FOR_GCC13),
    ),
    "bootstrap_v1.0": BootstrapStage (
        # target gcc-13, compiled with gcc-13, both on ubuntu 24.04
        prev_gyc="13_0.1.0",
        prev_gyllir="0.1.0",
        versions=GycVersions (compiler="13", target="13", ymir="1.0.0", bootstrap="1.0.0", midgard="1.0.0"),
        ubuntu_version=UBUNTU_FOR_GCC13,
        gyllir=GyllirSpec (gyc="13_1.0.0", compile_with="13", gyllir_version="1.0.0", ubuntu_version=UBUNTU_FOR_GCC13),
    ),
    "bootstrap_v1.1": BootstrapStage (
        # target gcc-15, but still compiled with gcc-13 (single ubuntu axis picks the compiler's
        # ubuntu here, since that's what fetch_gcc_version/configure/make need)
        prev_gyc="13_1.0.0",
        prev_gyllir="1.0.0",
        versions=GycVersions (compiler="13", target="15", ymir="1.1.0", bootstrap="1.1.0", midgard="1.1.0"),
        ubuntu_version=UBUNTU_FOR_GCC13,
        # install_gyc here installs the just-built gcc-15-targeted deb, so it needs the target's
        # ubuntu (26.04), not the compiler's (24.04) used to build it above.
        gyllir=GyllirSpec (gyc="15_1.1.0", compile_with="15", gyllir_version="1.1.0", ubuntu_version=UBUNTU_FOR_GCC15),
    ),
    "bootstrap_v1.1.1": BootstrapStage (
        # target gcc-15, compiled with gcc-15, both on ubuntu 26.04
        prev_gyc="15_1.1.0",
        prev_gyllir="1.1.0",
        versions=GycVersions (compiler="15", target="15", ymir="1.1.0", bootstrap="1.1.1", midgard="1.1.1"),
        ubuntu_version=UBUNTU_FOR_GCC15,
        # gyllir 1.2.0 is self-built (see GyllirSpec.prev_gyllir) against the previous stage'self
        # released 1.1.0 gyllir.
        gyllir=GyllirSpec (gyc="15_1.1.1", compile_with="15", gyllir_version="1.2.0", ubuntu_version=UBUNTU_FOR_GCC15, prev_gyllir="1.1.0"),
    ),
    "bootstrap_v1.2.3": BootstrapStage (
        # target gcc-15, compiled with gcc-15, both on ubuntu 26.04
        prev_gyc="15_1.1.1",
        prev_gyllir="1.1.0",
        versions=GycVersions (compiler="15", target="15", ymir="1.2.3", bootstrap="1.2.3", midgard="1.2.1"),
        ubuntu_version=UBUNTU_FOR_GCC15,
        gyllir=GyllirSpec (gyc="15_1.2.3", compile_with="15", gyllir_version="1.3.1", ubuntu_version=UBUNTU_FOR_GCC15, prev_gyllir="1.2.0"),
    ),
    "bootstrap_v1.3.2": BootstrapStage (
        # target gcc-15, compiled with gcc-15, both on ubuntu 26.04
        prev_gyc="15_1.2.3",
        prev_gyllir="1.3.1",
        versions=GycVersions (compiler="15", target="15", ymir="1.3.2", bootstrap="1.3.2", midgard="1.3.0"),
        ubuntu_version=UBUNTU_FOR_GCC15,
        gyllir=GyllirSpec(gyc="15_1.3.2", compile_with="15", gyllir_version="1.5.1", ubuntu_version=UBUNTU_FOR_GCC15, prev_gyllir="1.3.1"),
    ),
    "bootstrap_v1.4.0": BootstrapStage (
        # target gcc-15, compiled with gcc-15, both on ubuntu 26.04
        prev_gyc="15_1.3.2",
        prev_gyllir="1.5.1",
        versions=GycVersions (compiler="15", target="15", ymir="1.4.0", bootstrap="1.4.0", midgard="1.3.6"),
        ubuntu_version=UBUNTU_FOR_GCC15,
        gyllir=GyllirSpec(gyc="15_1.4.0", compile_with="15", gyllir_version="1.7.0", ubuntu_version=UBUNTU_FOR_GCC15, prev_gyllir="1.5.1"),
    ),
    "bootstrap_v1.5.3": BootstrapStage (
        # target gcc-15, compiled with gcc-15, both on ubuntu 26.04
        prev_gyc="15_1.4.0",
        prev_gyllir="1.7.0",
        versions=GycVersions (compiler="15", target="15", ymir="1.5.3", bootstrap="1.5.3", midgard="1.6.0"),
        ubuntu_version=UBUNTU_FOR_GCC15,
        gyllir=GyllirSpec(gyc="15_1.5.3", compile_with="15", gyllir_version="1.8.0", ubuntu_version=UBUNTU_FOR_GCC15, prev_gyllir="1.7.0"),
    ),
    "bootstrap_v1.6.0": BootstrapStage (
        # target gcc-15, compiled with gcc-15, both on ubuntu 26.04. ymir1 links
        # -lgymidgard-debug_1.6, the midgard gyc 1.5.3's .deb already bundles.
        prev_gyc="15_1.5.3",
        prev_gyllir="1.8.0",
        versions=GycVersions (compiler="15", target="15", ymir="1.6.0", bootstrap="1.6.0", midgard="1.8.0"),
        ubuntu_version=UBUNTU_FOR_GCC15,
        # No gyllir release after 1.8.0 (already built by bootstrap_v1.5.3).
    ),
    "bootstrap_v1.7.0": BootstrapStage (
        # target gcc-15, compiled with gcc-15, both on ubuntu 26.04. bootstrap 1.7.0 pins std
        # 1.9.0, which ymir1 links, but gyc 1.6.0's .deb only carries midgard 1.8 - so 1.9.0 is
        # built with it first (see GycVersions.bootstrap_midgard).
        prev_gyc="15_1.6.0",
        prev_gyllir="1.8.0",
        versions=GycVersions (compiler="15", target="15", ymir="1.7.0", bootstrap="1.7.0", midgard="1.10.0", bootstrap_midgard="1.9.0"),
        ubuntu_version=UBUNTU_FOR_GCC15,
        # No gyllir release after 1.8.0 (already built by bootstrap_v1.5.3).
    ),
    "bootstrap_v1.8.0": BootstrapStage (
        # target gcc-15, compiled with gcc-15, both on ubuntu 26.04. bootstrap 1.7.0 pins std
        # 1.9.0, which ymir1 links, but gyc 1.6.0's .deb only carries midgard 1.8 - so 1.9.0 is
        # built with it first (see GycVersions.bootstrap_midgard).
        prev_gyc="15_1.7.0",
        prev_gyllir="1.8.0",
        versions=GycVersions (compiler="15", target="15", ymir="1.8.0", bootstrap="1.8.0", midgard="1.12.0"),
        ubuntu_version=UBUNTU_FOR_GCC15,
    ),
}
