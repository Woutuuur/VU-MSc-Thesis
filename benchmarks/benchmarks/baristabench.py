from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
import re
import subprocess

from benchmarks.benchmark import Benchmark, BenchmarkUnit
from util.color import ANSIColorCode as C
from benchmarks.compiler import Compiler
from benchmarks.optimization_level import OptimizationLevel


@dataclass
class BaristaBenchmark(Benchmark):
    context_path: Path = field(default = Path("/data/baristabench"))
    n_runs: int = field(default = 2)
    unit: BenchmarkUnit = field(default = BenchmarkUnit.THROUGHPUT, init = False)

    def __post_init__(self):
        if not subprocess.run(["which", "python3"], stdout = subprocess.DEVNULL).returncode == 0:
            raise EnvironmentError("Python3 is not available in the PATH. Please install Python3.")

    @property
    def jar_path(self) -> Path:
        return self.context_path / Path(".")
    
    @property
    def config_dir(self) -> Path:
        return self.context_path / f"{self.name}-config"

    @property
    def benchmark_dir(self) -> Path:
        return self.context_path / "benchmarks" / self.name

    @cached_property
    def nib_file_path(self) -> Path:
        command = [
            "python3", (self.context_path / "build.py").absolute().as_posix(),
            "--get-nib", self.name,
        ]
        output = subprocess.check_output(
            [x for x in command if x],
            text = True,
            stderr = subprocess.STDOUT
        )
        if not (m := re.search(r"^application nib file path is: (.*)$", output, re.MULTILINE)):
            raise RuntimeError(f"Could not find application nib file path in command output: {output}")
        nib_file = Path(m.group(1))
        if not nib_file.exists():
            raise FileNotFoundError(f"Nib file does not exist: {nib_file}\n\n{output}")

        return nib_file

    @staticmethod
    def _extract_result(output: str) -> float:
        warmup, final = re.findall(r".*Measures for throughput iteration 1:\n.*throughput *(\d+\.\d+) ops/s", output, re.MULTILINE)

        return float(final)

    def run_agent(self, vm_binary: str = "java") -> int:
        return 0 # We expect to already have a .nib file in the target directory

    def build_native_image(self, compiler: Compiler, optimization_level = OptimizationLevel.O3, additional_build_args: list[str] = []) -> int:
        command = [
            *compiler.get_command(self.options).split(),
            optimization_level.value,
            "-H:+PlatformInterfaceCompatibilityMode",
            *self.native_image_args,
            *additional_build_args,
            "-march=native",
            f"--bundle-apply={self.nib_file_path.as_posix()}",
            "-o", self.name,
        ]
        print(f"{C.GRAY}Building native image with command: {' '.join(command)}{C.ENDC}")

        try:
            output = subprocess.check_output(
                [x for x in command if x],
                text = True,
                stderr = subprocess.STDOUT
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to build native image: {e.output}") from e

        if not (m := re.search(r"Bundle build output written to (.*)", output, re.MULTILINE)):
            raise RuntimeError(f"Could not find bundle build output in command output: {output}")
        
        binary_path = Path(m.group(1)) / 'default' / self.name

        if not binary_path.exists():
            raise FileNotFoundError(f"Binary does not exist after build: {binary_path}")

        self.binary_path.unlink(missing_ok = True)
        self.binary_path.symlink_to(binary_path)

        return 0

    def _get_run_command(self, additional_args: list[str] = []) -> list[str]:
        return [
            "python3", (self.context_path / "barista.py").absolute().as_posix(),
            "--mode", "native",
            self.name,
            *self.benchmark_runner_args,
            *self.benchmark_args,
            f"--app-args=\"{' '.join(additional_args)}\"" if additional_args else "",
            "-x", self.binary_path.absolute().as_posix(),
        ]
