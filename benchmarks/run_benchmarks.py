import csv
import sys
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from collections import defaultdict
from benchmarks.compiler import Compiler
from benchmarks.job import BenchmarkJob, read_jobs_from_config_file
from benchmarks.optimization_level import OptimizationLevel
from util.color import ANSIColorCode as C
from benchmarks.benchmark import Benchmark, BenchmarkResult, read_benchmarks_from_file
from config.config import Config
import statistics


def run_benchmark(benchmark: Benchmark) -> list[BenchmarkResult]:
    runs: list[BenchmarkResult] = []
    for _ in range(benchmark.n_runs):
        print(".", end="", flush=True)
        runs.append(benchmark.run())
    print("")

    return runs


def build_native_image(benchmark: Benchmark, optimization_level: OptimizationLevel, compiler: Compiler) -> None:
    rename_log = True

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
        case OptimizationLevel.CUSTOM_PGO_O3_NO_DYN_INVOKE_IC:
            benchmark.build_pgo_optimized_binary(compiler, additional_build_args=["-J-DcombinedInlining=true", "-J-DdisableInlineCachePhase=true", "-O3"])
        case OptimizationLevel.CUSTOM_PGO_FULL_O3_ONLY_IC:
            benchmark.build_pgo_optimized_binary(compiler, additional_build_args=["-J-DoriginalInlining=true", "-O3"])
        case _:
            rename_log = False
            _ = benchmark.build_native_image(
                compiler,
                optimization_level,
                additional_build_args=["-J-DdisableVirtualInvokeProfilingPhase=true"],
            )

    # Hack because we have optimization level NONE for PGO builds, so have to rename it back to the requested optimization level
    if rename_log:
        original_log_path = benchmark.get_log_path(compiler, OptimizationLevel.NONE)
        _ = original_log_path.rename(benchmark.get_log_path(compiler, optimization_level))


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
                    writer.writerow({
                        "benchmark": name,
                        "optimization_level": job.optimization_level.value,
                        "result": r.result,
                        "binary_size": r.binary_size,
                        "compiler": job.compiler.name,
                    })

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

    config = Config.from_file(config_file_path)

    if config.options.dump_profiling_data:
        config.options.profiling_data_output_dir_path.mkdir(parents=True, exist_ok=True)

    benchmarks = read_benchmarks_from_file(config.options.benchmarks_file_path, config.options)
    jobs_by_compiler = read_jobs_from_config_file(config_file_path, benchmarks)

    config.check_installations()

    results: ResultsDict = defaultdict(lambda: defaultdict(list))

    for i, (name, jobs) in enumerate(jobs_by_compiler.items()):
        print(C.BOLD + "=" * 20 + f" {name} ({i + 1}/{len(jobs_by_compiler)}) " + "=" * 20 + C.ENDC)

        if not jobs:
            continue

        def line_prefix(idx: int) -> str:
            return f"{C.BOLD}[{idx}/{len(jobs)}] [{cur_time()}]{C.ENDC}"

        if not config.options.skip_agent:
            print(f"{line_prefix(0)} Running agent for {name}...")
            _ = jobs[0].benchmark.run_agent(vm_binary=config.options.java_bin_path.as_posix())

        start_time = datetime.now()

        for i, job in enumerate(jobs):
            try:
                print(f"{line_prefix(i + 1)} Building using {C.BOLD}{job.compiler.name.lower().replace('_', ' ')}{C.ENDC} native image with optimization level {C.BOLD}{job.optimization_level.value}{C.ENDC}...")
                build_native_image(job.benchmark, job.optimization_level, job.compiler)

                print(f"{C.GRAY}Running benchmark {name} with command: {' '.join(job.benchmark._get_run_command())}{C.ENDC}")
                print(f"{line_prefix(i + 1)} Running benchmark {name} {job.benchmark.n_runs} time(s)", end="", flush=True)
                runs = run_benchmark(job.benchmark)
                results[name][job].extend(runs)
            except Exception as e:
                print(f"{C.FAIL}\nError while processing {name} with {job.compiler.name} at optimization level {job.optimization_level.value}: {e}{C.ENDC}")

        duration = (datetime.now() - start_time).seconds
        print(f"{C.OKBLUE}Finished processing {name} in {duration // 60}m {duration % 60}s{C.ENDC}")

    write_results_to_csv(results, config.options.results_output_dir_path / "results.csv")

    for name, result in results.items():
        print(f"Results for {C.BOLD}{name}{C.BOLD}:")
        for job, benchmark_results in result.items():
            if not benchmark_results:
                continue

            raw_results = [r.result for r in benchmark_results]
            average_result = f"{statistics.mean(raw_results):>10.2f}"
            stddev_result  = f"± {statistics.stdev(raw_results):>8.2f}"
            median_result  = f"(med. {statistics.median(raw_results):.2f})"

            compiler_name = f"{job.compiler.name.replace('_', ' ').capitalize():<12}"
            optimization_level = f"{job.optimization_level.value:>34}"
            size = f"size: {benchmark_results[0].binary_size:>10} bytes"
            unit = f"{job.benchmark.unit.value:<5}"

            print(f"  {compiler_name} {optimization_level}: {average_result} {median_result:>12} {stddev_result} {unit} {size}")

if __name__ == "__main__":
    main()
