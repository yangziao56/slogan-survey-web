#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build Part 2 blocks with per-question lures.
"""

from __future__ import annotations

import csv
import json
import random
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

PART2_LURE_SEED = 2026
LURES_PER_QUESTION = 2


def fnv1a32(text: str) -> int:
    h = 0x811C9DC5
    for b in text.encode("utf-8"):
        h ^= b
        h = (h * 0x01000193) & 0xFFFFFFFF
    return h


def extract_model_name(filename: str) -> str:
    name = filename.replace(".csv", "")
    name = re.sub(r"_\d{8}_\d{6}$", "", name)
    name = name.replace("_results", "").replace("_extracted", "")
    return name


def find_generation_columns(fieldnames: Sequence[str]) -> List[str]:
    cols = [c for c in fieldnames if c.startswith("Generation_")]

    def key(c: str) -> int:
        m = re.match(r"Generation_(\d+)$", c)
        return int(m.group(1)) if m else 10**9

    return sorted(cols, key=key)


@dataclass(frozen=True)
class ModelTable:
    model_name: str
    source_path: Path
    rows: List[Dict[str, str]]
    generation_cols: List[str]


def read_csv_rows(path: Path) -> Tuple[List[str], List[Dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(f"Missing header: {path}")
        rows: List[Dict[str, str]] = []
        for r in reader:
            rows.append({k: (v if v is not None else "") for k, v in r.items()})
        return list(reader.fieldnames), rows


def load_models(results_clean_dir: Path) -> Dict[str, ModelTable]:
    csv_files = sorted(results_clean_dir.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found under: {results_clean_dir}")
    models: Dict[str, ModelTable] = {}
    for fp in csv_files:
        fieldnames, rows = read_csv_rows(fp)
        model_name = extract_model_name(fp.name)
        gen_cols = find_generation_columns(fieldnames)
        models[model_name] = ModelTable(
            model_name=model_name,
            source_path=fp,
            rows=rows,
            generation_cols=gen_cols,
        )
    return models


def choose_lure(
    *,
    model_row: Dict[str, str],
    generation_cols: Sequence[str],
    source_col: str,
    old_text: str,
    seed_key: str,
) -> str:
    candidates: List[str] = []
    for col in generation_cols:
        if col == source_col:
            continue
        text = (model_row.get(col) or "").strip()
        if not text:
            continue
        if text == old_text:
            continue
        candidates.append(text)
    if not candidates:
        return old_text
    rng = random.Random(fnv1a32(seed_key))
    return candidates[rng.randrange(len(candidates))]


def main() -> None:
    web_root = Path(__file__).resolve().parent
    survey_root = web_root.parent
    repo_root = survey_root.parent

    stage_b_path = survey_root / "stage_b_bank_blocks.csv"
    results_clean_dir = repo_root / "results_clean"
    out_dir = web_root / "part2_blocks"
    out_dir.mkdir(parents=True, exist_ok=True)

    models = load_models(results_clean_dir)

    rows: List[Dict[str, str]] = []
    with stage_b_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)

    blocks: Dict[int, List[Dict[str, object]]] = {}
    for row in rows:
        block_id = int(row["block_id"])
        qid = int(row["question_id"])
        scenario_id = int(row["scenario_id"])

        labels = ["A", "B", "C", "D"]
        rng = random.Random(fnv1a32(f"{PART2_LURE_SEED}|{qid}|labels"))
        labels_shuf = labels[:]
        rng.shuffle(labels_shuf)
        lure_labels = set(labels_shuf[:LURES_PER_QUESTION])

        options = []
        for label in labels:
            model_name = row[f"option_{label}_model"]
            source_col = row[f"option_{label}_source_col"]
            old_text = (row[f"option_{label}_slogan"] or "").strip()
            if model_name not in models:
                raise ValueError(f"Missing model table for: {model_name}")
            model = models[model_name]
            if scenario_id >= len(model.rows):
                raise ValueError(f"Scenario out of range: {scenario_id} for {model_name}")
            model_row = model.rows[scenario_id]

            expected_old = (model_row.get(source_col) or "").strip()
            if expected_old and expected_old != old_text:
                raise ValueError(
                    f"Slogan mismatch qid={qid} label={label} model={model_name}: "
                    f"stage_b='{old_text}' results_clean='{expected_old}'"
                )

            text = old_text
            if label in lure_labels:
                seed_key = f"{PART2_LURE_SEED}|{qid}|{label}|lure"
                text = choose_lure(
                    model_row=model_row,
                    generation_cols=model.generation_cols,
                    source_col=source_col,
                    old_text=old_text,
                    seed_key=seed_key,
                )

            options.append({"label": label, "text": text})

        question = {
            "question_id": qid,
            "scenario_id": scenario_id,
            "brand": row["brand"],
            "persona": row["persona"],
            "options": options,
        }
        blocks.setdefault(block_id, []).append(question)

    for block_id, questions in sorted(blocks.items()):
        questions_sorted = sorted(questions, key=lambda x: x["question_id"])
        out = {
            "block_id": block_id,
            "questions": questions_sorted,
        }
        out_path = out_dir / f"block_{block_id:02d}.json"
        out_path.write_text(
            json.dumps(out, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    meta = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "seed": PART2_LURE_SEED,
        "lures_per_question": LURES_PER_QUESTION,
        "stage_b_bank_blocks_csv": str(stage_b_path.relative_to(repo_root)),
        "results_clean_dir": str(results_clean_dir.relative_to(repo_root)),
        "model_files": [str(p.name) for p in sorted(results_clean_dir.glob("*.csv"))],
        "num_blocks": len(blocks),
        "num_questions": sum(len(v) for v in blocks.values()),
    }
    meta_path = web_root / "part2_metadata.json"
    meta_path.write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Wrote {out_dir} (n={len(blocks)})")
    print(f"Wrote {meta_path}")


if __name__ == "__main__":
    main()
