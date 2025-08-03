from enum import Enum

from config import GRAALVM_HOME, GRAALVM_OPEN_HOME

class Compiler(Enum):
    OPEN   = (GRAALVM_OPEN_HOME / "bin" / "native-image").absolute().as_posix()
    CLOSED = (GRAALVM_HOME      / "bin" / "native-image").absolute().as_posix()
    CUSTOM_OPEN = "mx -p /workspace/graal/substratevm native-image"
