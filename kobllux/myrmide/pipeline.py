from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Sequence
import random

MYRMIDE_LAW = "VERDADE × INTEGRAR ÷ Δ = ♾️"

@dataclass(frozen=True)
class SeedSpec:
    identifier: str
    size: int = 33

SEEDS: Sequence[SeedSpec] = (
    SeedSpec("SCIART_5804762293847872985_sz33"),
    SeedSpec("SCIART_2467743094302853421_sz33"),
    SeedSpec("SCIART_7189249979715475219_sz33"),
)

VISUAL_GLYPHS = [" ", ".", ":", "*", "+", "o", "O", "#", "@".strip()]
ADJUSTMENT_GLYPHS = VISUAL_GLYPHS + list("1234567")

BASE_DIR = Path("MYRMIDE")
UNO_DIR = BASE_DIR / "UNO"
DUAL_DIR = BASE_DIR / "DUAL"
TRINITY_DIR = BASE_DIR / "TRINITY"
HUB_DIR = BASE_DIR / "HUB"
SEALS_DIR = UNO_DIR / "SEALS" / "items"

Pair = Sequence[str]


def _seed_to_int(identifier: str) -> int:
    digits = "".join(ch for ch in identifier if ch.isdigit())
    return int(digits) if digits else 0


def _ensure_dirs(paths: Iterable[Path]) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def _build_matrix(seed: SeedSpec) -> List[List[str]]:
    rng = random.Random(_seed_to_int(seed.identifier))
    half = seed.size // 2
    top_rows: List[List[str]] = []
    for _ in range(half):
        left = [rng.choice(VISUAL_GLYPHS) for _ in range(half)]
        center = rng.choice(VISUAL_GLYPHS) if seed.size % 2 else ""
        row = left + ([center] if center else []) + list(reversed(left))
        top_rows.append(row)
    center_row: List[str]
    if seed.size % 2:
        left = [rng.choice(VISUAL_GLYPHS) for _ in range(half)]
        center = rng.choice(VISUAL_GLYPHS)
        center_row = left + [center] + list(reversed(left))
        matrix = top_rows + [center_row] + list(reversed(top_rows))
    else:
        matrix = top_rows + list(reversed(top_rows))
    return _enforce_delta7(matrix)


def _matrix_checksum(matrix: List[List[str]]) -> int:
    return sum(ord(ch) for row in matrix for ch in row)


def _enforce_delta7(matrix: List[List[str]]) -> List[List[str]]:
    size = len(matrix)
    if size == 0:
        return matrix
    checksum = _matrix_checksum(matrix)
    remainder = checksum % 7
    if remainder == 0:
        return matrix
    centre = size // 2
    candidates: List[tuple[int, int]] = []
    if size % 2:
        candidates.append((centre, centre))
    candidates.extend((centre, idx) for idx in range(size))
    candidates.extend((idx, centre) for idx in range(size))
    candidates.extend((i, j) for i in range(size) for j in range(size))

    for i, j in candidates:
        original = matrix[i][j]
        for glyph in ADJUSTMENT_GLYPHS:
            if glyph == original:
                continue
            updated = checksum - ord(original) + ord(glyph)
            if updated % 7 == 0:
                matrix[i][j] = glyph
                return matrix
    return matrix


def _matrix_to_text(matrix: List[List[str]]) -> str:
    return "\n".join("".join(row) for row in matrix) + "\n"


def _flip_horizontal(matrix: List[List[str]]) -> List[List[str]]:
    return [list(reversed(row)) for row in matrix]


def _flip_vertical(matrix: List[List[str]]) -> List[List[str]]:
    return list(reversed(matrix))


def _rotate_180(matrix: List[List[str]]) -> List[List[str]]:
    return [list(reversed(row)) for row in reversed(matrix)]


def _character_counts(matrix: List[List[str]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for row in matrix:
        for char in row:
            counts[char] = counts.get(char, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: (item[0] != " ", item[0])))


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _relative(path: Path) -> str:
    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        return str(path)


def _write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _write_json(path: Path, payload: Dict) -> None:
    _write_text(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def _build_report(seed: SeedSpec, matrix: List[List[str]], ascii_path: Path, mirrors: Dict[str, Path]) -> Dict:
    checksum = _matrix_checksum(matrix)
    counts = _character_counts(matrix)
    report = {
        "seed": seed.identifier,
        "size": seed.size,
        "law": MYRMIDE_LAW,
        "delta7": {
            "checksum": checksum % 7,
            "valid": checksum % 7 == 0,
        },
        "palindrome": {
            "horizontal": all(row == list(reversed(row)) for row in matrix),
            "vertical": matrix == list(reversed(matrix)),
        },
        "characters": {
            "unique": list(counts.keys()),
            "counts": counts,
        },
        "paths": {
            "ascii": _relative(ascii_path),
            "mirrors": {name: _relative(path) for name, path in mirrors.items()},
        },
        "hash": _sha256(_matrix_to_text(matrix)),
    }
    return report


def _build_markdown(seed: SeedSpec, matrix: List[List[str]], report: Dict) -> str:
    ascii_block = _matrix_to_text(matrix)
    glyphs = ", ".join(report["characters"]["unique"])
    return (
        f"# MYRMIDE Seed — {seed.identifier}\n\n"
        f"- Lei: {MYRMIDE_LAW}\n"
        f"- Tamanho: {seed.size}×{seed.size}\n"
        f"- Delta7 válido: {report['delta7']['valid']}\n"
        f"- Glifos únicos: {glyphs}\n"
        "\n"
        "```text\n"
        f"{ascii_block}"
        "```\n"
    )


def _seal_payload(seed: SeedSpec, report: Dict) -> Dict:
    return {
        "seed": seed.identifier,
        "delta7": report["delta7"],
        "hash": report["hash"],
        "issued_at": datetime.now(timezone.utc).isoformat(),
        "seal": "∆7",
        "law": MYRMIDE_LAW,
        "note": "Selagem fractal validada pelo pipeline MYRMIDE.",
    }


def _pair_payload(pair: Pair, reports: Dict[str, Dict]) -> Dict:
    a, b = pair
    combined_hash = _sha256(reports[a]["hash"] + reports[b]["hash"])
    return {
        "pair": list(pair),
        "bridge": f"{a} ↔ {b}",
        "fusion_hash": combined_hash,
        "delta7_vector": [reports[a]["delta7"]["checksum"], reports[b]["delta7"]["checksum"]],
        "palindrome_memory": bool(reports[a]["palindrome"]["horizontal"] and reports[b]["palindrome"]["horizontal"]),
        "issued_at": datetime.now(timezone.utc).isoformat(),
    }


def _triple_payload(reports: Dict[str, Dict]) -> Dict:
    seed_ids = [seed.identifier for seed in SEEDS]
    fused_signature = _sha256("".join(reports[seed]["hash"] for seed in seed_ids))
    six_poles = [
        [seed_ids[0], seed_ids[1]],
        [seed_ids[1], seed_ids[2]],
        [seed_ids[2], seed_ids[0]],
    ]
    return {
        "seeds": seed_ids,
        "six_poles": six_poles,
        "fusion_signature": fused_signature,
        "delta7_vector": [reports[seed]["delta7"]["checksum"] for seed in seed_ids],
        "palindrome_cluster": all(reports[seed]["palindrome"]["horizontal"] for seed in seed_ids),
        "issued_at": datetime.now(timezone.utc).isoformat(),
    }


def _hub_manifest(reports: Dict[str, Dict], pair_paths: Dict[str, str], triple_path: str) -> Dict:
    return {
        "law": MYRMIDE_LAW,
        "layers": {
            "UNO": {seed: report["paths"] for seed, report in reports.items()},
            "DUAL": pair_paths,
            "TRINITY": triple_path,
        },
        "validation": {
            seed: report["delta7"] for seed, report in reports.items()
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def _hub_loop(reports: Dict[str, Dict]) -> Dict:
    return {
        "cycle": "UNO → DUAL → TRINITY → HUB",
        "law": MYRMIDE_LAW,
        "palindrome_checks": {
            seed: {
                "horizontal": report["palindrome"]["horizontal"],
                "vertical": report["palindrome"]["vertical"],
            }
            for seed, report in reports.items()
        },
        "status": "stable",
        "loops": 1,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def run_pipeline(base_dir: Path | None = None) -> None:
    if base_dir is None:
        base_dir = BASE_DIR
    uno_dir = base_dir / "UNO"
    dual_dir = base_dir / "DUAL"
    trinity_dir = base_dir / "TRINITY"
    hub_dir = base_dir / "HUB"
    seals_dir = uno_dir / "SEALS" / "items"

    _ensure_dirs([uno_dir, dual_dir, trinity_dir, hub_dir, seals_dir])

    reports: Dict[str, Dict] = {}
    pair_paths: Dict[str, str] = {}

    for seed in SEEDS:
        seed_dir = uno_dir / seed.identifier
        original_dir = seed_dir / "original"
        mirror_h_dir = seed_dir / "mirror_h"
        mirror_v_dir = seed_dir / "mirror_v"
        rot_dir = seed_dir / "rot180"
        _ensure_dirs([seed_dir, original_dir, mirror_h_dir, mirror_v_dir, rot_dir])

        matrix = _build_matrix(seed)
        ascii_text = _matrix_to_text(matrix)
        ascii_path = original_dir / f"{seed.identifier}.ascii.txt"
        _write_text(ascii_path, ascii_text)

        mirrors = {
            "mirror_h": mirror_h_dir / f"{seed.identifier}.ascii.txt",
            "mirror_v": mirror_v_dir / f"{seed.identifier}.ascii.txt",
            "rot180": rot_dir / f"{seed.identifier}.ascii.txt",
        }

        _write_text(mirrors["mirror_h"], _matrix_to_text(_flip_horizontal(matrix)))
        _write_text(mirrors["mirror_v"], _matrix_to_text(_flip_vertical(matrix)))
        _write_text(mirrors["rot180"], _matrix_to_text(_rotate_180(matrix)))

        report = _build_report(seed, matrix, ascii_path, mirrors)
        reports[seed.identifier] = report

        markdown_path = original_dir / f"{seed.identifier}.md"
        report_path = original_dir / f"{seed.identifier}.report.json"
        _write_text(markdown_path, _build_markdown(seed, matrix, report))
        _write_json(report_path, report)

        seal_path = seals_dir / f"{seed.identifier}.delta7.seal.json"
        _write_json(seal_path, _seal_payload(seed, report))

    pairs: Sequence[Pair] = (
        (SEEDS[0].identifier, SEEDS[1].identifier),
        (SEEDS[1].identifier, SEEDS[2].identifier),
        (SEEDS[2].identifier, SEEDS[0].identifier),
    )

    pair_dir = dual_dir / "pairs"
    _ensure_dirs([pair_dir])
    for pair in pairs:
        filename = "__".join(pair) + ".pair.json"
        path = pair_dir / filename
        _write_json(path, _pair_payload(pair, reports))
        pair_paths[" ↔ ".join(pair)] = _relative(path)

    triple_payload = _triple_payload(reports)
    triple_path = trinity_dir / "SCIART_triple.json"
    _write_json(triple_path, triple_payload)

    manifest_path = hub_dir / "manifest.json"
    _write_json(manifest_path, _hub_manifest(reports, pair_paths, _relative(triple_path)))

    loop_path = hub_dir / "loop.json"
    _write_json(loop_path, _hub_loop(reports))


if __name__ == "__main__":  # pragma: no cover
    run_pipeline()
