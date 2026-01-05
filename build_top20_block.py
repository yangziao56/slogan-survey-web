#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a custom block with the top-20 QwQ questions for Part 1 and Part 2."""

from __future__ import annotations

import csv
import json
from copy import deepcopy
from pathlib import Path

TOP20_QIDS = [
    65,
    12,
    188,
    193,
    7,
    41,
    50,
    114,
    82,
    99,
    144,
    184,
    196,
    15,
    24,
    39,
    74,
    84,
    131,
    134,
]

OUT_BLOCK_ID = 10


def load_stage_b_rows(path: Path) -> dict[int, dict[str, str]]:
    rows = {}
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            qid = int(row["question_id"])
            rows[qid] = row
    return rows


def load_part2_questions(part2_dir: Path) -> dict[int, dict]:
    questions = {}
    for fp in sorted(part2_dir.glob("block_*.json")):
        data = json.loads(fp.read_text(encoding="utf-8"))
        for q in data.get("questions", []):
            qid = int(q["question_id"])
            questions[qid] = q
    return questions


def main() -> None:
    web_root = Path(__file__).resolve().parent
    survey_root = web_root.parent

    stage_b_path = survey_root / "stage_b_bank_blocks.csv"
    part2_dir = web_root / "part2_blocks"
    blocks_dir = web_root / "blocks"

    stage_rows = load_stage_b_rows(stage_b_path)
    part2_questions = load_part2_questions(part2_dir)

    missing = [qid for qid in TOP20_QIDS if qid not in stage_rows]
    if missing:
        raise SystemExit(f"Missing question_id(s) in stage_b_bank_blocks.csv: {missing}")

    missing_p2 = [qid for qid in TOP20_QIDS if qid not in part2_questions]
    if missing_p2:
        raise SystemExit(f"Missing question_id(s) in part2_blocks: {missing_p2}")

    questions_part1 = []
    for display_id, qid in enumerate(TOP20_QIDS, start=1):
        row = stage_rows[qid]
        question = {
            "question_id": qid,
            "display_id": display_id,
            "source_block_id": int(row["block_id"]),
            "scenario_id": int(row["scenario_id"]),
            "brand": row["brand"],
            "persona": row["persona"],
            "options": [
                {"label": "A", "text": row["option_A_slogan"]},
                {"label": "B", "text": row["option_B_slogan"]},
                {"label": "C", "text": row["option_C_slogan"]},
                {"label": "D", "text": row["option_D_slogan"]},
            ],
        }
        questions_part1.append(question)

    questions_part2 = []
    for display_id, qid in enumerate(TOP20_QIDS, start=1):
        base = deepcopy(part2_questions[qid])
        base["display_id"] = display_id
        base["source_block_id"] = int(stage_rows[qid]["block_id"])
        questions_part2.append(base)

    blocks_dir.mkdir(parents=True, exist_ok=True)
    part2_dir.mkdir(parents=True, exist_ok=True)

    out_part1 = {
        "block_id": OUT_BLOCK_ID,
        "questions": questions_part1,
    }
    out_part2 = {
        "block_id": OUT_BLOCK_ID,
        "questions": questions_part2,
    }

    (blocks_dir / f"block_{OUT_BLOCK_ID:02d}.json").write_text(
        json.dumps(out_part1, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (part2_dir / f"block_{OUT_BLOCK_ID:02d}.json").write_text(
        json.dumps(out_part2, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Wrote blocks/block_{OUT_BLOCK_ID:02d}.json with {len(questions_part1)} questions")
    print(f"Wrote part2_blocks/block_{OUT_BLOCK_ID:02d}.json with {len(questions_part2)} questions")


if __name__ == "__main__":
    main()
