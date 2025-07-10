from abc import ABC, abstractmethod
from enum import Enum
from numbers import Number
from dataclasses import dataclass, field
from pathlib import Path
from optimization_level import OptimizationLevel

class BenchmarkUnit(Enum):
    EXECUTION_TIME = "ms"
    THROUGHPUT = "ops/sec"
    BINARY_SIZE = "bytes"

    def __str__(self) -> str:
        return self.value


@dataclass
class BenchmarkResult:
    name: str
    result: float
    binary_size: int
    output: str = field(repr = False)


@dataclass
class Benchmark(ABC):
    name: str
    context_path: Path
    unit: BenchmarkUnit
    n_runs: int = field(default = 1)
    native_image_args: list[str] = field(default_factory = list)
    benchmark_runner_args: list[str] = field(default_factory = list)
    benchmark_args: list[str] = field(default_factory = list)

    @property
    def binary_path(self) -> Path:
        return self.context_path / f"{self.name}"

    def _get_binary_size(self):
        if not self.binary_path.exists():
            raise FileNotFoundError(f"Binary does not exist: {self.binary_path}")

        return self.binary_path.stat().st_size

    @abstractmethod
    def run_agent(self, vm_binary: str = "java") -> int:
        pass

    @abstractmethod
    def build_native_image(self, native_image_binary: str = "native-image", optimization_level = OptimizationLevel.O3, additional_build_args: list[str] = []) -> int:
        pass

    @abstractmethod
    def build_pgo_optimized_binary(self, native_image_binary: str = "native-image") -> None:
        pass

    @abstractmethod
    def _run_benchmark(self, additional_args: list[str] = []) -> BenchmarkResult:
        pass

    def run(self, log = True) -> BenchmarkResult:
        result = self._run_benchmark()

        if log:
            with open(self.context_path / f"{self.name}.log", "a") as log_file:
                log_file.write(result.output)
        
        return result

1