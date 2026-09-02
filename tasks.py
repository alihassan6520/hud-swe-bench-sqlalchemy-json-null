from __future__ import annotations

import os
import shlex
import sys
from pathlib import Path

from hud.graders import BashGrader
from hud.graders import EvaluationResult
from hud.graders import SubScore
from hud.graders import combine

import env as env_mod
from coding import repo as repo_lib
from env import LOGS_DIR
from env import REPO_DIR
from env import VAULT_DIR
from env import WORKSPACE_NOTE
from env import _setup
from env import env


env_mod.REPO_URL = "https://github.com/sqlalchemy/sqlalchemy.git"

PROMPT = (Path(__file__).parent / "task" / "prompt.md").read_text()
GOLD_DIFF = Path(os.environ.get("GOLD_DIFF", "/hud/gold.diff"))
BASE_REF = "5462cec4c5b97ae9c1cefc0a0e022d49273b32e0"
BLOCKER_CAP = 0.70

GRADERS = [
    ("json_null_equality", 0.05, True, "bash", 300),
    ("json_null_inequality", 0.05, True, "bash", 300),
    ("nested_path_support", 0.05, True, "bash", 300),
    ("membership_support", 0.05, True, "bash", 300),
    ("reverse_operand_support", 0.05, True, "bash", 300),
    ("is_operator_support", 0.20, True, "bash", 300),
    ("mixed_membership_support", 0.20, True, "bash", 300),
    ("compiled_sql_shape", 0.15, False, "bash", 300),
    ("regression_backcompat", 0.05, False, "bash", 300),
    ("test_quality", 0.10, False, "bash", 300),
    ("maintainer_review", 0.05, False, "bash", 300),
]

_GRADER_SRC = Path(os.environ.get("GRADER_DIR", "/hud/grader"))
if not (_GRADER_SRC / "run_grading.sh").is_file():
    _GRADER_SRC = Path(__file__).parent / "task" / "grader"
GRADER = str(_GRADER_SRC / "run_grading.sh")


def _slim_metadata(subscores: list[SubScore]) -> None:
    for score in subscores:
        meta = getattr(score, "metadata", None)
        if not meta:
            continue
        for key in ("stdout", "stderr"):
            value = meta.get(key)
            if isinstance(value, str) and len(value) > 2500:
                meta[key] = "..." + value[-2500:]


async def _grade(validate_mode: str | None) -> EvaluationResult:
    setup_commit = await repo_lib.restore_history(REPO_DIR, VAULT_DIR)
    if validate_mode == "golden":
        diff = GOLD_DIFF.read_text()
    else:
        diff = await repo_lib.capture_agent_diff(REPO_DIR, setup_commit)

    if not diff.strip():
        return EvaluationResult(reward=0.0, content="Empty diff: no changes were made.")

    await repo_lib.reset_worktree(REPO_DIR, setup_commit)
    apply_error = await repo_lib.apply_diff(REPO_DIR, diff, LOGS_DIR / "patch.diff")
    if apply_error is not None:
        return EvaluationResult(
            reward=0.0,
            content="patch failed to apply",
            info={"git_apply": apply_error},
        )

    subscores: list[SubScore] = []
    for name, weight, _blocker, _kind, timeout in GRADERS:
        subscores.append(
            await BashGrader.grade(
                weight,
                name=name,
                command=(
                    f"PYTHON_BIN={shlex.quote(sys.executable)} "
                    f"bash {shlex.quote(GRADER)} {shlex.quote(name)}"
                ),
                cwd=str(REPO_DIR),
                timeout_seconds=timeout,
            )
        )

    _slim_metadata(subscores)
    result = await combine(*subscores)

    failed = sorted(
        name
        for name, _weight, blocker, _kind, _timeout in GRADERS
        if blocker and next(s.value for s in subscores if s.name == name) < 1.0
    )
    if failed:
        reward = min(result.reward, BLOCKER_CAP)
        return EvaluationResult(
            reward=reward,
            subscores=result.subscores,
            info={
                **result.info,
                "uncapped_reward": result.reward,
                "failed_blockers": failed,
            },
            content=(
                f"Blocker criteria failed ({', '.join(failed)}); "
                f"reward capped at {reward:.3f}."
            ),
        )

    return result


@env.template(
    id="sqlite_json_null_comparison",
    description="Make SQLite JSON.NULL path comparisons distinguish JSON null from absent paths.",
)
async def sqlite_json_null_comparison(validate_mode: str | None = None):
    if validate_mode not in (None, "golden"):
        raise ValueError(f"unknown validate_mode: {validate_mode!r}")
    await _setup(BASE_REF)
    if validate_mode == "golden":
        _ = yield "Golden-validation run: no work is expected. Finish immediately."
    else:
        _ = yield f"{WORKSPACE_NOTE}\n\n{PROMPT}"
    yield await _grade(validate_mode)


tasks = [sqlite_json_null_comparison()]
