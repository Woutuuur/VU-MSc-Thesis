import os
from pathlib import Path

GRAALVM_HOME = Path(os.environ.get("GRAALVM_HOME", "None"))
GRAALVM_OPEN_HOME = Path(os.environ.get("GRAALVM_OPEN_HOME", "None"))
OUTPUT_DIR = Path(".").absolute()
JAVA_HOME = Path(os.environ.get("JAVA_HOME", ""))
JAVA_BIN_PATH = GRAALVM_HOME / "bin" / "java"
N_RUNS = 5
SKIP_AGENT = False
