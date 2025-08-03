from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from benchmarks.baristabench import BaristaBenchmark
from benchmarks.benchmark import Benchmark, BenchmarkResult, BenchmarkUnit
from benchmarks.dacapobench import DacapoBenchmark
from color import Color
from compiler import Compiler
from config import JAVA_BIN, OUTPUT_DIR, SKIP_AGENT, check_environment
from optimization_level import OptimizationLevel
import csv
from datetime import datetime
from zoneinfo import ZoneInfo

LU_RUNNER_ARGS = [
    "-Dorg.apache.lucene.store.MMapDirectory.enableMemorySegments=false",
    "--no-validation"
]

BENCHMARKS = [
    DacapoBenchmark("avrora",   benchmark_args = ["-t", "1"]),
    DacapoBenchmark("batik",    benchmark_args = ["-t", "1"]),
    DacapoBenchmark("biojava",  benchmark_args = ["-t", "1"]),
    DacapoBenchmark("graphchi", benchmark_args = ["-t", "1"]),
    DacapoBenchmark("h2",       benchmark_args = ["-t", "1"]),
    DacapoBenchmark("sunflow",  benchmark_args = ["-t", "1"]),
    DacapoBenchmark("lusearch", benchmark_runner_args = LU_RUNNER_ARGS),
    DacapoBenchmark("luindex",  benchmark_runner_args = LU_RUNNER_ARGS),
    DacapoBenchmark("pmd",      benchmark_runner_args = ["--no-validation"]),
    DacapoBenchmark("xalan",    native_image_args = [
        "--initialize-at-build-time=org.apache.crimson.parser.Parser2,"
        "org.apache.crimson.parser.Parser2\\$Catalog,"
        "org.apache.crimson.parser.Parser2\\$NullHandler,"
        "org.apache.xml.utils.res.CharArrayWrapper"
    ]),

    BaristaBenchmark("micronaut-shopcart"),
    BaristaBenchmark("micronaut-hello-world"),
    BaristaBenchmark("micronaut-similarity"),
]

@dataclass
class BenchmarkJob:
    benchmark: Benchmark
    optimization_level: OptimizationLevel
    compiler: Compiler

CLOSED_SOURCE_JOBS = {
    benchmark.name: tuple(
        BenchmarkJob(benchmark, optimization_level, Compiler.CLOSED)
        for optimization_level in [
            OptimizationLevel.SIZE,
            OptimizationLevel.O0,
            OptimizationLevel.O3,
            OptimizationLevel.PGO
        ]
    )
    for benchmark in BENCHMARKS
}

OPEN_SOURCE_JOBS = {
    benchmark.name: tuple(
        BenchmarkJob(benchmark, optimization_level, Compiler.OPEN)
        for optimization_level in [
            OptimizationLevel.SIZE,
            OptimizationLevel.O0,
            OptimizationLevel.O3
        ]
    )
    for benchmark in BENCHMARKS
}

CUSTOM_OPEN_SOURCE_JOBS = {
    benchmark.name: tuple(
        BenchmarkJob(benchmark, optimization_level, Compiler.CUSTOM_OPEN)
        for optimization_level in [
            OptimizationLevel.SIZE,
            OptimizationLevel.O0,
            OptimizationLevel.O3,
            OptimizationLevel.CUSTOM_PGO,
            OptimizationLevel.CUSTOM_PGO_O3,
            OptimizationLevel.CUSTOM_PGO_FULL,
            OptimizationLevel.CUSTOM_PGO_FULL_O3
        ]
    )
    for benchmark in BENCHMARKS
}

ALL_JOBS = {
    benchmark.name: CUSTOM_OPEN_SOURCE_JOBS[benchmark.name] + CLOSED_SOURCE_JOBS[benchmark.name] + OPEN_SOURCE_JOBS[benchmark.name]
    for benchmark in BENCHMARKS
}

def run_benchmark(benchmark: Benchmark) -> list[BenchmarkResult]:
    runs = []
    for _ in range(benchmark.n_runs):
        print(".", end='', flush=True)
        runs.append(benchmark.run())
    print("")

    return runs

def build_native_image(benchmark: Benchmark, optimization_level: OptimizationLevel, compiler: Compiler) -> None:
    match optimization_level:
        case OptimizationLevel.PGO:
            benchmark.build_pgo_optimized_binary(compiler) # Closed source PGO determines optimization level itself
        case OptimizationLevel.CUSTOM_PGO:
            benchmark.build_pgo_optimized_binary(compiler, additional_build_args=["-O0"])
        case OptimizationLevel.CUSTOM_PGO_O3:
            benchmark.build_pgo_optimized_binary(compiler, additional_build_args=["-O3"])
        case OptimizationLevel.CUSTOM_PGO_FULL:
            benchmark.build_pgo_optimized_binary(compiler, additional_build_args=["-J-DcombinedInlining=true", "-O0"])
        case OptimizationLevel.CUSTOM_PGO_FULL_O3:
            benchmark.build_pgo_optimized_binary(compiler, additional_build_args=["-J-DcombinedInlining=true", "-O3"])
        case _:
            benchmark.build_native_image(compiler, optimization_level, additional_build_args=["-J-DdisableVirtualInvokeProfilingPhase=true"])

ResultsDict = dict[str, dict[tuple[OptimizationLevel, Compiler], list[BenchmarkResult]]]

def write_results_to_csv(results: ResultsDict, output_file: Path) -> None:
    with open(output_file, "w", newline='') as csvfile:
        fieldnames = ["benchmark", "optimization_level", "result", "binary_size", "compiler"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for name, result in results.items():
            for (optimization_level, compiler), benchmark_results in result.items():
                for r in benchmark_results:
                    writer.writerow({
                        "benchmark": name,
                        "optimization_level": optimization_level.value,
                        "result": r.result,
                        "binary_size": r.binary_size,
                        "compiler": compiler.name
                    })

def cur_time() -> str:
    return datetime.now(tz=ZoneInfo("Europe/Amsterdam")).strftime("%H:%M:%S")

def main():
    check_environment()

    results: ResultsDict = defaultdict(lambda: defaultdict(list))

    for i, (name, jobs) in enumerate(ALL_JOBS.items()):
        print(Color.BOLD + "=" * 20 + f" {name} ({i + 1}/{len(ALL_JOBS)}) " + "=" * 20 + Color.ENDC)

        if not jobs:
            continue

        def line_prefix(i) -> str:
            return f"{Color.BOLD}[{i}/{len(jobs)}] [{cur_time()}]{Color.ENDC}"

        if not SKIP_AGENT:
            print(f"{line_prefix(0)} Running agent for {name}...")
            jobs[0].benchmark.run_agent(vm_binary = JAVA_BIN.as_posix())

        start_time = datetime.now()

        for i, job in enumerate(jobs):
            try:
                print(f"{line_prefix(i + 1)} Building using {Color.BOLD}{job.compiler.name.lower().replace('_', ' ')}{Color.ENDC} native image with optimization level {Color.BOLD}{job.optimization_level.value}{Color.ENDC}...")
                build_native_image(job.benchmark, job.optimization_level, job.compiler)

                print(f"{Color.GRAY}Running benchmark {name} with command: {' '.join(job.benchmark._get_run_command())}{Color.ENDC}")
                print(f"{line_prefix(i + 1)} Running benchmark {name} {job.benchmark.n_runs} time(s)", end='', flush=True)
                runs = run_benchmark(job.benchmark)
                results[name][(job.optimization_level, job.compiler)].extend(runs)
            except Exception as e:
                print(f"{Color.FAIL}\nError while processing {name} with {job.compiler.name} at optimization level {job.optimization_level.value}: {e}{Color.ENDC}")

        duration = (datetime.now() - start_time).seconds
        print(f"{Color.OKBLUE}Finished processing {name} in {duration // 60}m {duration % 60}s{Color.ENDC}")

    for name, result in results.items():
        print(f"Results for {Color.BOLD}{name}{Color.BOLD}:")
        for (optimization_level, compiler), benchmark_results in result.items():
            average_result = sum(r.result for r in benchmark_results) / len(benchmark_results)
            stddev_result = (sum((r.result - average_result) ** 2 for r in benchmark_results) / len(benchmark_results)) ** 0.5
            print(f"  {compiler.name.replace('_', ' ').capitalize():<12} {optimization_level.value:>28}: {average_result:>10.2f} ± {stddev_result:>7.2f} {job.benchmark.unit.value:<5} size: {benchmark_results[0].binary_size:>10} bytes")

    write_results_to_csv(results, OUTPUT_DIR / "results.csv")

if __name__ == "__main__":
    main()
