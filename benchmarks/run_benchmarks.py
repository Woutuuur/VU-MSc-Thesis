import csv
import re
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
import shutil


def run_benchmark(benchmark: Benchmark) -> list[BenchmarkResult]:
    runs: list[BenchmarkResult] = []
    for _ in range(benchmark.n_runs):
        print(".", end="", flush=True)
        runs.append(benchmark.run())
    print("")

    return runs


# Returns compilation time in seconds
def build_native_image(benchmark: Benchmark, optimization_level: OptimizationLevel, compiler: Compiler) -> float:
    rename_log = True
    out = ""

    match optimization_level:
        case OptimizationLevel.PGO:
            out = benchmark.build_pgo_optimized_binary(compiler)  # Closed source PGO determines optimization level itself
        case OptimizationLevel.CUSTOM_PGO:
            out = benchmark.build_pgo_optimized_binary(compiler, additional_build_args=["-O0"])
        case OptimizationLevel.CUSTOM_PGO_O3:
            out = benchmark.build_pgo_optimized_binary(compiler, additional_build_args=["-O3"])
        case OptimizationLevel.CUSTOM_PGO_FULL:
            out = benchmark.build_pgo_optimized_binary(compiler, additional_build_args=["-J-DcombinedInlining=true", "-O0"])
        case OptimizationLevel.CUSTOM_PGO_FULL_O3:
            out = benchmark.build_pgo_optimized_binary(compiler, additional_build_args=["-J-DcombinedInlining=true", "-O3"])
        case OptimizationLevel.CUSTOM_PGO_O3_NO_DYN_INVOKE_IC:
            out = benchmark.build_pgo_optimized_binary(compiler, additional_build_args=["-J-DcombinedInlining=true", "-J-DdisableInlineCachePhase=true", "-O3"])
        case OptimizationLevel.CUSTOM_PGO_FULL_O3_ONLY_IC:
            out = benchmark.build_pgo_optimized_binary(compiler, additional_build_args=["-J-DoriginalInlining=true", "-O3"])
        case OptimizationLevel.CUSTOM_FULL_COMPILER_PROFILING:
            out = benchmark.build_pgo_optimized_binary(compiler, additional_build_args=["-J-DcombinedInlining=true", "-O3", "-J-DprofileCompiler=true"])
        case OptimizationLevel.CUSTOM_FULL_COMPILER_PGO:
            out = benchmark.build_pgo_optimized_binary(compiler, additional_build_args=["-J-DcombinedInlining=true", "-O3", "-J-DuseCompilerPGO=true"])
        case _:
            rename_log = False
            out = benchmark.build_native_image(
                compiler,
                optimization_level,
                additional_build_args=["-J-DdisableVirtualInvokeProfilingPhase=true"],
            )
    
    # E.g.:
    # Finished generating 'sunflow' in 22.9s.
    # Finished generating 'pmd' in 1m 4s.
    build_time_match = re.search(f"Finished generating '{benchmark.name}' in ((?:([0-9]+)m )?([0-9.]+)s).", str(out))
    if not build_time_match:
        raise RuntimeError(f"Could not determine build time from output:\n{out}")
    
    # Parse the time components
    minutes_str = build_time_match.group(2)  # Could be None if no minutes
    seconds_str = build_time_match.group(3)  # Always present
    
    minutes = int(minutes_str) if minutes_str else 0
    seconds = float(seconds_str)
    build_time_seconds = minutes * 60 + seconds

    # Hack because we have optimization level NONE for PGO builds, so have to rename it back to the requested optimization level
    if rename_log:
        original_log_path = benchmark.get_log_path(compiler, OptimizationLevel.NONE)
        _ = original_log_path.rename(benchmark.get_log_path(compiler, optimization_level))

    return build_time_seconds


ResultsDict = dict[str, dict[BenchmarkJob, list[BenchmarkResult]]]
BenchmarkTimesResultsDict = dict[str, dict[BenchmarkJob, list[float]]]



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
    compilation_time_results: BenchmarkTimesResultsDict = defaultdict(lambda: defaultdict(list))

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
                for _ in range(config.options.n_compilations):
                    compilation_time_results[name][job].append(build_native_image(job.benchmark, job.optimization_level, job.compiler))

                # Copy binary to results/current/binaries with optimization level and compiler name in the name
                binary_output_dir = config.options.results_output_dir_path / "binaries"
                binary_output_dir.mkdir(parents=True, exist_ok=True)
                binary_output_path = binary_output_dir / f"{name}_{job.compiler.name.lower()}_{job.optimization_level.value}"
                shutil.copy(job.benchmark.binary_path, binary_output_path)

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
            if not benchmark_results and not compilation_time_results:
                continue

            benchmarks_stats = ""
            if benchmark_results:
                size = f"size: {benchmark_results[0].binary_size:>10} bytes"
                unit = f"{job.benchmark.unit.value:<5}"

                raw_results = [r.result for r in benchmark_results]
                average_result = f"{statistics.mean(raw_results):>10.2f}"
                stddev_result  = f"± {statistics.stdev(raw_results):>8.2f}" if len(raw_results) > 2 else ""
                median_result  = f"(med. {statistics.median(raw_results):.2f})"
                benchmarks_stats = f"{average_result} {median_result:>12} {stddev_result} {unit} {size}"

            compilation_time_stats = ""
            if compilation_time_results and config.options.show_compilation_times:
                raw_results = compilation_time_results[name][job]
                average_compilation_time = f"{statistics.mean(raw_results):.2f}s"
                stddev_compilation_time = f"± {statistics.stdev(raw_results):.2f}s" if len(raw_results) > 2 else ""
                compilation_time_stats = f"comp. time: {average_compilation_time} {stddev_compilation_time}"

            compiler_name = f"{job.compiler.name.replace('_', ' ').capitalize():<12}"
            optimization_level = f"{job.optimization_level.value:>34}"
            print(f"  {compiler_name} {optimization_level}: {benchmarks_stats}, {compilation_time_stats}")

if __name__ == "__main__":
    main()
