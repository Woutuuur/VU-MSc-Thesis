from dataclasses import dataclass, field
from pathlib import Path
import re
import subprocess
from benchmarks.benchmark import Benchmark, BenchmarkUnit
from util.color import ANSIColorCode as C
from benchmarks.compiler import Compiler
from benchmarks.optimization_level import OptimizationLevel


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
    def _extract_result(output: str) -> float:
        if m := re.search(r".* in (\d+) msec .*", output, re.MULTILINE):
            return float(m.group(1))

        raise ValueError(f"Could not extract execution time from output: {output}")

    def run_agent(self, vm_binary: str = "java") -> int:
        return subprocess.call([
            vm_binary,
            f"-agentlib:native-image-agent=config-output-dir={self.config_dir.absolute().as_posix()}",
            "-jar", self.jar_path.as_posix(), 
            self.name
        ], stderr = subprocess.STDOUT, stdout = subprocess.DEVNULL, cwd = self.context_path.as_posix())

    def build_native_image(self, compiler: Compiler, optimization_level = OptimizationLevel.O3, additional_build_args = []) -> int:
        command = [
            *compiler.get_command(self.options).split(),
            optimization_level.value,
            "-H:+PlatformInterfaceCompatibilityMode",
            f"-H:ConfigurationFileDirectories=./{self.config_dir.relative_to(self.context_path).as_posix()}",
            *self.native_image_args,
            *additional_build_args,
            "-jar", self.jar_path.as_posix(),
            "-march=native",
        ]
        print(f"{C.GRAY}Building native image with command: {' '.join(command)}{C.ENDC}")
        return subprocess.call(command, stderr = subprocess.STDOUT, stdout = subprocess.DEVNULL, cwd = self.context_path.as_posix())

    def _get_run_command(self, additional_args: list[str] = []) -> list[str]:
        return [
            self.binary_path.absolute().as_posix(),
            *self.benchmark_runner_args,
            self.name,
            *self.benchmark_args,
            *additional_args
        ]

@dataclass
class FopBenchmark(DacapoBenchmark):
    def __post_init__(self):
        self.config_dir.mkdir(parents = True, exist_ok = True)

        fop_config = self.config_dir / "empty"
        subprocess.call(["touch", fop_config.as_posix()])

        self.native_image_args.extend([
            f"-Djava.util.logging.config.file={fop_config.as_posix()}"
        ])
