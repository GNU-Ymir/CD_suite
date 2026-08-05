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
    - midgard: yruntime/midgard stdlib git tag.
    """
    compiler: str
    target: str
    ymir: str
    bootstrap: str
    midgard: str

    @property
    def compiler_major(self) -> str:
        return self.compiler.split(".")[0]

    @property
    def target_major(self) -> str:
        return self.target.split(".")[0]
