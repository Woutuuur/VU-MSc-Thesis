from enum import Enum

from config import GRAALVM_HOME, GRAALVM_OPEN_HOME


class Compiler(Enum):
    OPEN = (GRAALVM_OPEN_HOME / "bin" / "native-image").absolute().as_posix()
    CLOSED = (GRAALVM_HOME / "bin" / "native-image").absolute().as_posix()
    CUSTOM_OPEN = "mx -p /workspace/graal/substratevm native-image"


def check_environment(used_compilers: set[Compiler]) -> None:
    required_path_for_compilers = {
        Compiler.CLOSED: GRAALVM_HOME,
        Compiler.OPEN: GRAALVM_OPEN_HOME,
    }

    for compiler in used_compilers:
        if compiler not in required_path_for_compilers:
            continue

        required_path = required_path_for_compilers[compiler]
        if not required_path.exists():
            raise EnvironmentError(f"{compiler.name} path does not exist: {required_path}")
        if not required_path.is_dir():
            raise EnvironmentError(f"{compiler.name} path is not a directory: {required_path}")
