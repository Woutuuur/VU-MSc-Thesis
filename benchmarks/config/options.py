import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ConfigOptions:
    dump_profiling_data: bool = field(default=False)
    skip_agent: bool = field(default=False)
    skip_run: bool = field(default=False)
    skip_profiling: bool = field(default=False)
    graalvm_home: Path = field(default_factory=lambda: Path(os.environ.get("GRAALVM_HOME", "None")))
    graalvm_open_home: Path = field(default_factory=lambda: Path(os.environ.get("GRAALVM_OPEN_HOME", "None")))
    java_home: Path = field(default_factory=lambda: Path(os.environ.get("JAVA_HOME", "None")))
    benchmarks_file_path: Path = field(default=Path("configs") / "benchmarks.json")
    results_output_dir_base_path: Path = field(default=Path("results"))

    @property
    def results_output_dir_path(self) -> Path:
        return self.results_output_dir_base_path / "current"

    @property
    def profiling_data_output_dir_path(self) -> Path:
        return self.results_output_dir_path / "profiling-data"

    @property
    def java_bin_path(self) -> Path:
        return self.graalvm_home / "bin" / "java"
