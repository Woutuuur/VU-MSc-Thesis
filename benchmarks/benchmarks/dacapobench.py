from dataclasses import dataclass, field
from pathlib import Path
import re
import subprocess
from benchmarks.benchmark import Benchmark, BenchmarkResult, BenchmarkUnit
from optimization_level import OptimizationLevel


@dataclass
class DacapoBenchmark(Benchmark):
    version: str = field(default = "23.11-MR2")
    context_path: Path = field(default = Path("/data/dacapobench"))
    n_runs: int = field(default = 5)
    unit: BenchmarkUnit = field(default = BenchmarkUnit.EXECUTION_TIME, init = False)

    @property
    def launcher_dir(self) -> Path:
        return self.context_path / f"dacapo-{self.version}-chopin" / "launchers"

    @property
    def jar_path(self) -> Path:
        return self.launcher_dir / f"{self.name}.jar"
    
    @property
    def config_dir(self) -> Path:
        return self.context_path / f"{self.name}-config"

    @staticmethod
    def _extract_execution_time(output: str) -> float:
        if m := re.search(r".* in (\d+) msec .*", output, re.MULTILINE):
            return float(m.group(1))

        raise ValueError(f"Could not extract execution time from output: {output}")

    def run_agent(self, vm_binary: str = "java") -> int:
        return subprocess.call([
            vm_binary,
            f"-agentlib:native-image-agent=config-output-dir={self.config_dir.as_posix()}",
            "-jar", self.jar_path.as_posix(), 
            self.name
        ])

    def build_native_image(self, native_image_binary: str = "native-image", optimization_level = OptimizationLevel.O3, additional_build_args = []) -> int:
        return subprocess.call([
            *native_image_binary.split(),
            optimization_level.value,
            "-H:+PlatformInterfaceCompatibilityMode",
            "-J-DdisableVirtualInvokeProfilingPhase=true",
            f"-H:ConfigurationFileDirectories=./{self.config_dir.as_posix()}",
            *self.native_image_args,
            *additional_build_args,
            "-jar", self.jar_path.as_posix(),
            "-march=native",
        ], stdout=subprocess.DEVNULL)

    def build_pgo_optimized_binary(self, native_image_binary: str = "native-image") -> None:
        # Create instrumented binary
        self.build_native_image(
            native_image_binary=native_image_binary,
            optimization_level=OptimizationLevel.NONE,
            additional_build_args=["--pgo-instrument"]
        )

        prof_file_path = (self.context_path / f"{self.name}.iprof").as_posix()

        # Run the instrumented binary to collect profiling data
        self._run_benchmark(additional_args=[f"-XX:ProfilesDumpFile={prof_file_path}"])

        # Build the optimized binary using the collected profiling data
        self.build_native_image(
            native_image_binary=native_image_binary,
            optimization_level=OptimizationLevel.NONE,
            additional_build_args=[f"--pgo={prof_file_path}"]
        )

    def _run_benchmark(self, additional_args = []) -> BenchmarkResult:
        output = subprocess.check_output([
            self.binary_path.absolute().as_posix(),
            *self.benchmark_runner_args,
            self.name,
            *self.benchmark_args,
            *additional_args
        ], text=True, stderr=subprocess.STDOUT)
        execution_time = self._extract_execution_time(output)

        return BenchmarkResult(
            self.name,
            result=execution_time,
            binary_size=self._get_binary_size(),
            output=output
        )


@dataclass
class FopBenchmark(DacapoBenchmark):
    def __post_init__(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)

        fop_config = self.config_dir / "empty"
        subprocess.call(["touch", fop_config.as_posix()])

        self.native_image_args.extend([
            f"-Djava.util.logging.config.file={fop_config.as_posix()}"
        ])