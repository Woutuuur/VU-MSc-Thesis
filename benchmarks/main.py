from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import os
from benchmarks.baristabench import BaristaBenchmark
from benchmarks.benchmark import Benchmark, BenchmarkResult, BenchmarkUnit
from benchmarks.dacapobench import DacapoBenchmark
from optimization_level import OptimizationLevel
import csv

OUTPUT_DIR = Path(".").absolute()
GRAALVM_HOME = Path(os.environ.get("GRAALVM_HOME", "None"))
GRAALVM_OPEN_HOME = Path(os.environ.get("GRAALVM_OPEN_HOME", "None"))
JAVA_HOME = Path(os.environ.get("JAVA_HOME", ""))
JAVA_BIN = JAVA_HOME / "bin" / "java"
N_RUNS = 5

LU_RUNNER_ARGS = [
    "-Dorg.apache.lucene.store.MMapDirectory.enableMemorySegments=false",
    "--no-validation"
]

BENCHMARKS = [
    # DacapoBenchmark("avrora",   benchmark_args = ["-t", "1"]),
    # DacapoBenchmark("batik",    benchmark_args = ["-t", "1"]),
    # DacapoBenchmark("biojava",  benchmark_args = ["-t", "1"]),
    # DacapoBenchmark("graphchi", benchmark_args = ["-t", "1"]),
    # DacapoBenchmark("h2",       benchmark_args = ["-t", "1"]),
    # DacapoBenchmark("sunflow",  benchmark_args = ["-t", "1"]),
    # DacapoBenchmark("lusearch", benchmark_runner_args = LU_RUNNER_ARGS),
    # DacapoBenchmark("luindex",  benchmark_runner_args = LU_RUNNER_ARGS),
    # DacapoBenchmark("pmd",      benchmark_runner_args = ["--no-validation"]),
    # DacapoBenchmark("xalan",    native_image_args = [
    #     "--initialize-at-build-time=org.apache.crimson.parser.Parser2,"
    #     "org.apache.crimson.parser.Parser2\\$Catalog,"
    #     "org.apache.crimson.parser.Parser2\\$NullHandler,"
    #     "org.apache.xml.utils.res.CharArrayWrapper"
    # ]),

    # BaristaBenchmark("helidon-hello-world"),
    # BaristaBenchmark("ktor-hello-world"),
    BaristaBenchmark("micronaut-hello-world"),
    BaristaBenchmark("micronaut-shopcart"),
    BaristaBenchmark("micronaut-similarity"),
    # BaristaBenchmark("play-scala-hello-world"),
    BaristaBenchmark("quarkus-hello-world"),
    BaristaBenchmark("quarkus-tika"),
    BaristaBenchmark("spring-hello-world"),
    BaristaBenchmark("spring-petclinic"),
    BaristaBenchmark("vanilla-hello-world"),
    BaristaBenchmark("vertx-hello-world")
]

SKIP_AGENT = True

def check_environment():
    if not GRAALVM_HOME.exists():
        raise EnvironmentError(f"GRAALVM_HOME does not exist: {GRAALVM_HOME}")
    if not GRAALVM_HOME.is_dir():
        raise EnvironmentError(f"GRAALVM_HOME is not a directory: {GRAALVM_HOME}")
    if not GRAALVM_OPEN_HOME.exists():
        raise EnvironmentError(f"GRAALVM_OPEN_HOME does not exist: {GRAALVM_OPEN_HOME}")
    if not GRAALVM_OPEN_HOME.is_dir():
        raise EnvironmentError(f"GRAALVM_OPEN_HOME is not a directory: {GRAALVM_OPEN_HOME}")
    if not JAVA_HOME.exists():
        raise EnvironmentError(f"JAVA_HOME does not exist: {JAVA_HOME}")
    if not JAVA_HOME.is_dir():
        raise EnvironmentError(f"JAVA_HOME is not a directory: {JAVA_HOME}")


class Compiler(Enum):
    # OPEN   = "mx -p /workspace/graal/substratevm native-image"
    OPEN   = (GRAALVM_OPEN_HOME / "bin" / "native-image").absolute().as_posix()
    CLOSED = (GRAALVM_HOME      / "bin" / "native-image").absolute().as_posix()

@dataclass
class BenchmarkJob:
    benchmark: Benchmark
    optimization_level: OptimizationLevel
    compiler: Compiler

CLOSED_SOURCE_JOBS = {
    benchmark.name: tuple(
        BenchmarkJob(benchmark, optimization_level, Compiler.CLOSED)
        for optimization_level in [ OptimizationLevel.PGO]
    )
    for benchmark in BENCHMARKS
}

OPEN_SOURCE_JOBS = {
    benchmark.name: tuple(
        BenchmarkJob(benchmark, optimization_level, Compiler.OPEN)
        for optimization_level in [OptimizationLevel.SIZE, OptimizationLevel.O3]
    )
    for benchmark in BENCHMARKS
}

ALL_JOBS = {
    benchmark.name: CLOSED_SOURCE_JOBS[benchmark.name] 
    for benchmark in BENCHMARKS
}

def run_benchmark(benchmark: Benchmark) -> list[BenchmarkResult]:
    runs = []
    for _ in range(benchmark.n_runs):
        print(".", end='', flush=True)
        runs.append(benchmark.run())
    print("")

    return runs

def build_native_image(benchmark: Benchmark, optimization_level: OptimizationLevel, native_image_binary: str) -> None:
    match optimization_level:
        case OptimizationLevel.PGO:
            benchmark.build_pgo_optimized_binary(native_image_binary = native_image_binary)
        case _:
            benchmark.build_native_image(
                native_image_binary = native_image_binary,
                optimization_level = optimization_level
            )

ResultsDict = dict[str, dict[tuple[OptimizationLevel, Compiler], list[BenchmarkResult]]]

def write_results_to_csv(results: ResultsDict, output_file: Path) -> None:
    with open(OUTPUT_DIR / "results.csv", "w", newline='') as csvfile:
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

def main():
    check_environment()

    results: ResultsDict = defaultdict(lambda: defaultdict(list))

    for i, (name, jobs) in enumerate(ALL_JOBS.items()):
        print("=" * 20 + f" {name} ({i + 1}/{len(ALL_JOBS)}) " + "=" * 20)

        if not jobs:
            continue

        if not SKIP_AGENT:
            print(f"Running agent for {name}...")
            jobs[0].benchmark.run_agent(vm_binary = JAVA_BIN.as_posix())

        for i, job in enumerate(jobs):
            print(f"[{i + 1}/{len(jobs)}] Building using {job.compiler.name.lower()} source native image with optimization level {job.optimization_level.value}...")
            build_native_image(job.benchmark, job.optimization_level, job.compiler.value)

            print(f"[{i + 1}/{len(jobs)}] Running benchmark {name} {job.benchmark.n_runs} time(s)", end='', flush=True)
            runs = run_benchmark(job.benchmark)
            results[name][(job.optimization_level, job.compiler)].extend(runs)

    for name, result in results.items():
        print(f"Results for {name}:")
        for (optimization_level, compiler), benchmark_results in result.items():
            average_result = sum(r.result for r in benchmark_results) / len(benchmark_results)
            stddev_result = (sum((r.result - average_result) ** 2 for r in benchmark_results) / len(benchmark_results)) ** 0.5
            print(f"  {compiler.name.capitalize():<6} {optimization_level.value:>6}: {average_result:>10.2f} ± {stddev_result:>7.2f} {job.benchmark.unit.value:<5}, size: {benchmark_results[0].binary_size:>10} bytes")

    write_results_to_csv(results, OUTPUT_DIR / "results.csv")

if __name__ == "__main__":
    main()
