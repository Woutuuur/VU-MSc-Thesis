import json
from pathlib import Path
from typing import cast, TypedDict


class CallSiteProfile(TypedDict):
    receiverCounts: dict[str, int]
    totalCount: int
    isDirectCall: bool
    targetMethod: str


def load_json(file_path: Path) -> list[CallSiteProfile]:
    with open(file_path) as file:
        return cast(list[CallSiteProfile], json.load(file))

def expected_to_inline(profile: CallSiteProfile) -> bool:
    receiver_counts: dict[str, int] = profile["receiverCounts"]

    _highest_receiver, highest_receiver_count = next(iter(sorted(receiver_counts.items(), key=lambda x: x[1], reverse=True)))

    total_count = profile["totalCount"]
    proportion_highest = highest_receiver_count / total_count

    return not profile["isDirectCall"] and total_count > 10_000 and proportion_highest > 0.80


path = Path("results") / "current" / "profiling-data" / "avrora-custom_open.json"
data = load_json(path)

expected_to_inline_profiles = sorted(
    [profile for profile in data if expected_to_inline(profile)],
    key=lambda x: x["totalCount"]
)

print("{" + ",\n".join(f'\"{profile["targetMethod"]}\"' for profile in expected_to_inline_profiles) + "}")
print()
print("\n".join(str(profile) for profile in expected_to_inline_profiles))

print(len(expected_to_inline_profiles))
