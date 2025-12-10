from pathlib import Path
import re

benchmarks = [
    "avrora",
    "batik",
    "biojava",
    "graphchi",
    "h2",
    "sunflow",
    "lusearch",
    "luindex",
    "pmd",
    "xalan",
    "micronaut-shopcart",
    "micronaut-hello-world",
    "micronaut-similarity"
]
max_len_benchmark = max(len(b) for b in benchmarks)

log_dir = Path("results") / "current" / "logs"
for log_file in sorted(log_dir.glob("*.count.log"), key=lambda x: benchmarks.index(x.name.split('|')[0])):
    log = log_file.read_text()
    lines = '\n'.join(log.strip().split("\n"))

    total_sites =  int(re.search(r"Using top (\d+) call sites", lines, re.MULTILINE).group(1))
    indirect_sites_sites, direct_sites = map(int, re.search(r"Out of which (\d+) are indirect call sites and (\d+) are direct call sites", lines, re.MULTILINE).groups())
    indirect_calls, direct_calls = map(int, re.search(r"Representing (\d+) and (\d+) calls respectively", lines, re.MULTILINE).groups())
    total_calls = int(re.search(r"Total calls represented: (\d+)", lines, re.MULTILINE).group(1))
    
    percent_virtual_sites = indirect_sites_sites / total_sites * 100
    percent_virtual_calls = indirect_calls / total_calls * 100

    name = f"`{log_file.name.split('|')[0]}`"

    print(f"{name.ljust(max_len_benchmark + 2)}, ${total_sites:>4}$, ${percent_virtual_sites:>5.2f}%$, ${total_calls:>11}$, ${percent_virtual_calls:>5.2f}%$,")
