from collections import defaultdict
from pathlib import Path
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Generator, Generic, TypeVar

from benchmarks.compiler import Compiler
from benchmarks.optimization_level import OptimizationLevel
from util.color import ANSIColorCode as C

T = TypeVar('T')

def batched(l: list[T], n: int) -> Generator[list[T], None, None]:
    for i in range(0, len(l), n):
        yield l[i:i + n]

class InlineDecision(Enum):
    INLINED = "yes"
    NOT_INLINED = "no"

    @staticmethod
    def by_value(value: str) -> "InlineDecision":
        if value == "yes":
            return InlineDecision.INLINED
        elif value == "no":
            return InlineDecision.NOT_INLINED
        else:
            raise ValueError(f"Unknown inline decision value: {value}")

@dataclass(frozen=True)
class MethodCallInlineDecision:
    caller_name: str
    bci: int
    decision: InlineDecision
    decision_reason: str
    # location: str

InlinedMethodIdentifier = tuple[str, int]  # (caller, bci)

@dataclass(frozen=True)
class InlineLog:
    filename: str
    benchmark_name: str
    compiler: Compiler
    optimization_level: OptimizationLevel

    decisions: list[MethodCallInlineDecision] = field(default_factory=list, init=False, hash=False)
    
    def add_inline_decision(self, inline_decision: MethodCallInlineDecision):
        self.decisions.append(inline_decision)

    content: str = field(repr=False)

    def all_inlined_methods(self) -> Generator[InlinedMethodIdentifier, None, None]:
        for decision in self.decisions:
            if decision.decision == InlineDecision.INLINED:
                yield (decision.caller_name, decision.bci)

    def methods_inlined_in_both(self, other: "InlineLog") -> set[InlinedMethodIdentifier]:
        return set(self.all_inlined_methods()).intersection(set(other.all_inlined_methods()))

    def methods_inlined_only_in_self(self, other: "InlineLog") -> set[InlinedMethodIdentifier]:
        return set(self.all_inlined_methods()).difference(set(other.all_inlined_methods()))

    def methods_inlined_only_in_other(self, other: "InlineLog") -> set[InlinedMethodIdentifier]:
        return set(other.all_inlined_methods()).difference(set(self.all_inlined_methods()))

# phase, method, 
RE_DECISION = r".*<(GraphBuilderPhase|PEGraphDecoder)> (.*): (yes|no), (.*)"

def strip_address(caller: str) -> str:
    if m := re.match(r"(.*)\/0x[^\.]*\.(.*)", caller):
        a, b = m.groups()
        return f"{a}.{b}"

    return caller

def check_decision(caller: str, bci: int, line: str) -> MethodCallInlineDecision | None:
    # location = at.split('(')[1][:-1]

    if m := re.match(RE_DECISION, line):
        phase, method, decision, reason = m.groups()

        return MethodCallInlineDecision(strip_address(caller), bci,  InlineDecision(decision), reason)

    return None

def parse_inlining_decisions(blocks: list[str]) -> list[MethodCallInlineDecision]:
    decisions: list[MethodCallInlineDecision] = []
    for caller, content in batched(blocks, 2):
        stack = [(0, caller, -1)]
        for line in content.splitlines():
            if m := re.match(r"( +)(.*)", line):
                indent, line = m.groups()

                while stack[-1][0] > len(indent):
                    stack.pop()

                if m := re.match(r"at (.*) \[bci: (\d+)\]:(.*)$", line):
                    method, bci, suffix = map(str.strip, m.groups())
                    method = method.replace('%1', '')
                    bci = int(bci)
                    if suffix:
                        if d := check_decision(method, bci, suffix):
                            decisions.append(d)
                    else:
                        stack.append((len(indent), method, bci))
                elif len(stack) > 1:
                    # Check for <GraphBuilderPhase> and <PEGraphDecoder>
                    _, caller, bci = stack[-1]
                    if d := check_decision(caller, bci, line):
                        decisions.append(d)

    return decisions
    
def parse_bytecode_parser_inlining_decisions(content: str) -> list[MethodCallInlineDecision]:
    bytecode_parser_blocks: list[tuple[str, str, str]] = re.findall(r"^ *([^ ]+) \(([^\)]+)\) inlining call to ([^\n]+)$", content, re.MULTILINE)[1:]
    decisions = []
    for caller, location, callee in bytecode_parser_blocks:
        if location == "null:-1":
            continue

        decision = MethodCallInlineDecision(strip_address(caller), callee.strip(), InlineDecision.INLINED, "")
        decisions.append(decision)

    return units

def parse_inlining_log(log: InlineLog) -> None:
    head, *blocks = re.split(r"(?=compilation of (.*):)", log.content)
    blocks = blocks[:-1] + [blocks[-1].split('\n\n')[0]]

    for decision in parse_inlining_decisions(blocks):
        log.add_inline_decision(decision)

    for decision in parse_bytecode_parser_inlining_decisions(head):
        log.add_inline_decision(decision)

    # print(list(log.all_inlined_methods())[0], list(log.all_inlined_methods())[-1])

logs_by_benchmark: dict[str, list[InlineLog]] = defaultdict(list)

log_dir = Path("results") / "current" / "logs"
for log_path in log_dir.glob("*.log"):
    with open(log_path, "r") as f:
        benchmark_name, compiler_name, optimization_level = log_path.name.split('.')[0].split('|')
        log = InlineLog(log_path.name, benchmark_name, Compiler(compiler_name), OptimizationLevel(optimization_level), f.read())
        logs_by_benchmark[benchmark_name].append(log)

stats_by_benchmark = dict()

seen_opt_levels = set(y.optimization_level for x in logs_by_benchmark.values() for y in x)

for benchmark_name, logs in logs_by_benchmark.items():
    inlining_logs: list[InlineLog] = []
    print(f'{C.ENDC}{"=" * 25} {benchmark_name} {"=" * 25}')

    for log in logs:
        print(f"Parsing log: {log.filename}")
        units = []

        parse_inlining_log(log)
        inlining_logs.append(log)

    print("\nGeneral statistics:")
    for log in inlining_logs:
        total_inlined = len(set(log.all_inlined_methods()))
        print(f"{total_inlined:>10} total methods inlined in {C.BOLD}{log.optimization_level.value}{C.ENDC}")

    baseline = next(x for x in inlining_logs if x.optimization_level == OptimizationLevel.O3)
    others = set(inlining_logs) - {baseline}

    stats_by_benchmark[benchmark_name] = { log.optimization_level: dict() for log in inlining_logs }

    for log in others:
        print(f"\nComparing logs: {C.BOLD}{baseline.optimization_level.value}{C.ENDC} and {C.BOLD}{log.optimization_level.value}{C.ENDC}")
        only_in_first = baseline.methods_inlined_only_in_self(log)
        only_in_second = baseline.methods_inlined_only_in_other(log)
        in_both = baseline.methods_inlined_in_both(log)

        print(f"{len(only_in_first):>10} methods inlined only in {C.BOLD}{baseline.optimization_level.value}{C.ENDC}")
        print(f"{len(only_in_second):>10} methods inlined only in {C.BOLD}{log.optimization_level.value}{C.ENDC}")
        print(f"{len(in_both):>10} methods inlined in both")

        stats_by_benchmark[benchmark_name][log.optimization_level] = {
            "inlined_only_in_baseline": len(only_in_first),
            "inlined_only_in_this": len(only_in_second),
            "inlined_in_both": len(in_both)
        }
    print()

print("=" * 25, "Combined across all benchmarks", "=" * 25)
combined_stats: dict[OptimizationLevel, dict[str, int]] = { 
    optimization_level: {"inlined_only_in_baseline": 0, "inlined_only_in_this": 0, "inlined_in_both": 0} 
    for optimization_level in seen_opt_levels - {OptimizationLevel.O3} 
}

for benchmark_name, stats_by_optimization_level in stats_by_benchmark.items():
    for optimization_level, stats in stats_by_optimization_level.items():
        for key, value in stats.items():
            combined_stats[optimization_level][key] += value

for optimization_level, stats in combined_stats.items():
    print(f"\nStatistics for optimization level {C.BOLD}{optimization_level.value}{C.ENDC}:")
    for key, value in stats.items():
        print(f"{value:>10} methods {key.replace('_', ' ')}")
