from collections import defaultdict
from pathlib import Path
import re

base_path = Path("results") / "current" / "logs"
log_files = sorted(base_path.glob("*.log"), key = lambda x: x.name)

for log_file in log_files:
    with log_file.open("r") as file:
        data = file.read()
    
    no: dict[str, int] = defaultdict(int)
    yes: dict[str, int] = defaultdict(int)
    results: list[tuple[str, str]] = re.findall(r"\((High|Mid|Low|Other) tier\) .*: (yes|no)", data)
    for tier, result in results:
        if result == "yes":
            yes[tier] += 1
        else:
            no[tier] += 1
    print(log_file.name)
    for tier in sorted(set(no) | set(yes)):
        print(f"{tier:>8} tier {yes[tier]:>8} yes {no[tier]:>8} no")
    print()
