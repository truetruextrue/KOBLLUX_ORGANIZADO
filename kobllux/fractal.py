from typing import Dict, List
from .archetypes import ARCHETYPES

def triad_cycle(names: List[str]) -> List[List[str]]:
    if not names:
        return []
    triads = [names[i:i+3] for i in range(0, len(names), 3)]
    if len(triads[-1]) < 3:
        triads[-1] += names[:(3-len(triads[-1]))]
    out = []
    for step in range(3):
        for t in triads:
            out.append(t[step:] + t[:step])
    return out

def weave(depth: int = 2) -> Dict:
    names = list(ARCHETYPES.keys())
    levels, current = [], [names]
    for _ in range(depth):
        level = []
        for seq in current:
            level.extend(triad_cycle(seq))
        levels.append(level)
        current = level
    return {"depth": depth, "levels": levels}
