from enum import Enum


class OptimizationLevel(Enum):
    O0          = "-O0"
    O1          = "-O1"
    O2          = "-O2"
    O3          = "-O3"
    SIZE        = "-Os"
    BUILD_TIME  = "-Ob"
    PGO         = "--pgo"
    NONE        = ""
