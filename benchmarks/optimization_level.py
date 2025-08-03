from enum import Enum


class OptimizationLevel(Enum):
    O0         = "-O0"
    O1         = "-O1"
    O2         = "-O2"
    O3         = "-O3"
    SIZE       = "-Os"
    BUILD_TIME = "-Ob"

    PGO                = "--pgo"
    CUSTOM_PGO         = "--custom-pgo -O0"
    CUSTOM_PGO_O3      = "--custom-pgo -O3"
    CUSTOM_PGO_FULL    = "--custom-pgo -O0 (combined)"
    CUSTOM_PGO_FULL_O3 = "--custom-pgo -O3 (combined)"
    NONE               = ""
