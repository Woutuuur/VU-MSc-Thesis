import os
from pathlib import Path

GRAALVM_HOME = Path(os.environ.get("GRAALVM_HOME", "None"))
GRAALVM_OPEN_HOME = Path(os.environ.get("GRAALVM_OPEN_HOME", "None"))
OUTPUT_DIR = Path(".").absolute()
JAVA_HOME = Path(os.environ.get("JAVA_HOME", ""))
JAVA_BIN = GRAALVM_HOME / "bin" / "java"
N_RUNS = 5
SKIP_AGENT = False

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
