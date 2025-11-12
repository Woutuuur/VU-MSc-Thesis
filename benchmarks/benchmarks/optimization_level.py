from enum import Enum


class OptimizationLevel(Enum):
    O0 = "-O0"
    O1 = "-O1"
    O2 = "-O2"
    O3 = "-O3"
    SIZE = "-Os"
    BUILD_TIME = "-Ob"

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


# build-aot && mx -p /workspace/graal/substratevm native-image  -H:+PlatformInterfaceCompatibilityMode -H:ConfigurationFileDirectories=/data/dacapobench/avrora-config -H:ProfileDataDumpFileName=/workspace/benchmarks/results/current/profiling-data/avrora-custom_open.json -J-DdisableVirtualInvokeProfilingPhase=true -J-DcombinedInlining=true -O3 -jar /data/dacapobench/dacapo-23.11-MR2-chopin/launchers/avrora.jar -march=native --debug-attach
