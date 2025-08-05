from enum import Enum

from config.options import ConfigOptions


class Compiler(Enum):
    OPEN = "open"
    CLOSED = "closed"
    CUSTOM_OPEN = "custom_open"
    
    def get_command(self, options: ConfigOptions) -> str:
        match self:
            case Compiler.OPEN:
                return (options.graalvm_open_home / "bin" / "native-image").absolute().as_posix()
            case Compiler.CLOSED:
                return (options.graalvm_home / "bin" / "native-image").absolute().as_posix()
            case Compiler.CUSTOM_OPEN:
                return "mx -p /workspace/graal/substratevm native-image"
            case _:
                raise ValueError(f"Unknown compiler: {self.name}")
