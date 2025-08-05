import csv
import sys
from pathlib import Path
from datetime import datetime
from pprint import pprint
from zoneinfo import ZoneInfo
from collections import defaultdict
from benchmarks.job import BenchmarkJob, read_jobs_from_config_file
from color import ANSIColorCode as C
from compiler import Compiler, check_environment
from optimization_level import OptimizationLevel
from benchmarks.benchmark import Benchmark, BenchmarkResult, read_benchmarks_from_file
from config import BENCHMARKS_FILE_PATH, JAVA_BIN_PATH, OUTPUT_DIR, SKIP_AGENT


# LU_RUNNER_ARGS = [
#     "-Dorg.apache.lucene.store.MMapDirectory.enableMemorySegments=false",
#     "--no-validation",
# ]

# BENCHMARKS = [
#     DacapoBenchmark("avrora", benchmark_args=["-t", "1"]),
#     DacapoBenchmark("batik", benchmark_args=["-t", "1"]),
#     DacapoBenchmark("biojava", benchmark_args=["-t", "1"]),
#     DacapoBenchmark("graphchi", benchmark_args=["-t", "1"]),
#     DacapoBenchmark("h2", benchmark_args=["-t", "1"]),
#     DacapoBenchmark("sunflow", benchmark_args=["-t", "1"]),
#     DacapoBenchmark("lusearch", benchmark_runner_args=LU_RUNNER_ARGS),
#     DacapoBenchmark("luindex", benchmark_runner_args=LU_RUNNER_ARGS),
#     DacapoBenchmark("pmd", benchmark_runner_args=["--no-validation"]),
#     DacapoBenchmark("xalan", native_image_args=[
#         "--initialize-at-build-time=org.apache.crimson.parser.Parser2,"
#         "org.apache.crimson.parser.Parser2\\$Catalog,"
#         "org.apache.crimson.parser.Parser2\\$NullHandler,"
#         "org.apache.xml.utils.res.CharArrayWrapper"
#     ]),
#     BaristaBenchmark("micronaut-shopcart"),
#     BaristaBenchmark("micronaut-hello-world"),
#     BaristaBenchmark("micronaut-similarity"),
# ]


def run_benchmark(benchmark: Benchmark) -> list[BenchmarkResult]:
    runs = []
    for _ in range(benchmark.n_runs):
        print(".", end="", flush=True)
        runs.append(benchmark.run())
    print("")

    return runs


def build_native_image(benchmark: Benchmark, optimization_level: OptimizationLevel, compiler: Compiler) -> None:
    match optimization_level:
        case OptimizationLevel.PGO:
            benchmark.build_pgo_optimized_binary(compiler)  # Closed source PGO determines optimization level itself
        case OptimizationLevel.CUSTOM_PGO:
            benchmark.build_pgo_optimized_binary(compiler, additional_build_args=["-O0"])
        case OptimizationLevel.CUSTOM_PGO_O3:
            benchmark.build_pgo_optimized_binary(compiler, additional_build_args=["-O3"])
        case OptimizationLevel.CUSTOM_PGO_FULL:
            benchmark.build_pgo_optimized_binary(compiler, additional_build_args=["-J-DcombinedInlining=true", "-O0"])
        case OptimizationLevel.CUSTOM_PGO_FULL_O3:
            benchmark.build_pgo_optimized_binary(compiler, additional_build_args=["-J-DcombinedInlining=true", "-O3"])
        case _:
            benchmark.build_native_image(
                compiler,
                optimization_level,
                additional_build_args=["-J-DdisableVirtualInvokeProfilingPhase=true"],
            )


ResultsDict = dict[str, dict[BenchmarkJob, list[BenchmarkResult]]]


def write_results_to_csv(results: ResultsDict, output_file: Path) -> None:
    with open(output_file, "w", newline="") as csvfile:
        fieldnames = [
            "benchmark",
            "optimization_level",
            "result",
            "binary_size",
            "compiler",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for name, result in results.items():
            for job, benchmark_results in result.items():
                for r in benchmark_results:
                    writer.writerow(
                        {
                            "benchmark": name,
                            "optimization_level": job.optimization_level.value,
                            "result": r.result,
                            "binary_size": r.binary_size,
                            "compiler": job.compiler.name,
                        }
                    )


def cur_time() -> str:
    return datetime.now(tz=ZoneInfo("Europe/Amsterdam")).strftime("%H:%M:%S")


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <config_file_path.json>")
        sys.exit(1)

    config_file_path = Path(sys.argv[1])
    if not config_file_path.exists() or not config_file_path.is_file():
        print(f"Error: Config file '{config_file_path}' does not exist or is not a file.")
        sys.exit(1)

    benchmarks = read_benchmarks_from_file(BENCHMARKS_FILE_PATH)
    jobs_by_compiler = read_jobs_from_config_file(config_file_path, benchmarks)

    check_environment(set(job.compiler for jobs in jobs_by_compiler.values() for job in jobs))

    results: ResultsDict = defaultdict(lambda: defaultdict(list))

    for i, (name, jobs) in enumerate(jobs_by_compiler.items()):
        print(C.BOLD + "=" * 20 + f" {name} ({i + 1}/{len(jobs_by_compiler)}) " + "=" * 20 + C.ENDC)

        if not jobs:
            continue

        def line_prefix(idx) -> str:
            return f"{C.BOLD}[{idx}/{len(jobs)}] [{cur_time()}]{C.ENDC}"

        if not SKIP_AGENT:
            print(f"{line_prefix(0)} Running agent for {name}...")
            jobs[0].benchmark.run_agent(vm_binary=JAVA_BIN_PATH.as_posix())

        start_time = datetime.now()

        for i, job in enumerate(jobs):
            try:
                print(f"{line_prefix(i + 1)} Building using {C.BOLD}{job.compiler.name.lower().replace('_', ' ')}{C.ENDC} native image with optimization level {C.BOLD}{job.optimization_level.value}{C.ENDC}...")
                build_native_image(job.benchmark, job.optimization_level, job.compiler)

                print(f"{C.GRAY}Running benchmark {name} with command: {' '.join(job.benchmark._get_run_command())}{C.ENDC}")
                print(f"{line_prefix(i + 1)} Running benchmark {name} {job.benchmark.n_runs} time(s)...", end="", flush=True)
                runs = run_benchmark(job.benchmark)
                results[name][job].extend(runs)
            except Exception as e:
                print(f"{C.FAIL}\nError while processing {name} with {job.compiler.name} at optimization level {job.optimization_level.value}: {e}{C.ENDC}")

        duration = (datetime.now() - start_time).seconds
        print(f"{C.OKBLUE}Finished processing {name} in {duration // 60}m {duration % 60}s{C.ENDC}")

    for name, result in results.items():
        print(f"Results for {C.BOLD}{name}{C.BOLD}:")
        for job, benchmark_results in result.items():
            average_result = sum(r.result for r in benchmark_results) / len(benchmark_results)
            stddev_result = (sum((r.result - average_result) ** 2 for r in benchmark_results) / len(benchmark_results)) ** 0.5
            print(f"  {job.compiler.name.replace('_', ' ').capitalize():<12} {job.optimization_level.value:>28}: {average_result:>10.2f} ± {stddev_result:>7.2f} {job.benchmark.unit.value:<5} size: {benchmark_results[0].binary_size:>10} bytes")

    write_results_to_csv(results, OUTPUT_DIR / "results.csv")


if __name__ == "__main__":
    main()
