from dataclasses import dataclass, field
from enum import Enum
from typing import TypedDict

class OptimizationLevelConfig(TypedDict):
    label: str
    build_flags: list[str]
    load_dumped_prof_file: bool
    load_dumped_skippable_phases_file: bool

@dataclass(frozen=True)
class CustomOptimizationLevel:
    label: str = field(default="")
    build_flags: tuple[str, ...] = field(default_factory=tuple)
    load_dumped_prof_file: bool = field(default=False)
    load_dumped_skippable_phases_file: bool = field(default=False)

    @classmethod
    def from_optimization_level_config(cls, config: OptimizationLevelConfig) -> "CustomOptimizationLevel":
        load_dumped_prof_file = config.get("load_dumped_prof_file", False)
        load_dumped_skippable_phases_file = config.get("load_dumped_skippable_phases_file", False)

        return cls(
            config["label"],
            tuple(config["build_flags"]),
            load_dumped_prof_file,
            load_dumped_skippable_phases_file
        )

class OptimizationLevel(Enum):
    O0 = "-O0"
    O1 = "-O1"
    O2 = "-O2"
    O3 = "-O3"
    SIZE = "-Os"
    BUILD_TIME = "-Ob"

    INVOKE_PROFILING = "Invokes profiling"
    COMPILER_PROFILING = "Phase profiling"

    PGO = "--pgo"
    CUSTOM_PGO = "--custom-pgo -O0"
    CUSTOM_PGO_O3 = "--custom-pgo -O3"
    CUSTOM_PGO_FULL = "--custom-pgo -O0 (combined)"
    CUSTOM_PGO_FULL_O3 = "Combined"
    CUSTOM_PGO_FULL_O3_ONLY_IC = "Inline caches only"
    CUSTOM_PGO_O3_NO_DYN_INVOKE_IC = "Direct calls only"

    CUSTOM_FULL_COMPILER_PROFILING = "Compiler profiling"
    CUSTOM_FULL_COMPILER_PGO = "Compiler PGO"

    NONE = ""

    @property
    def label(self) -> str:
        return self.value
