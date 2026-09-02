#!/usr/bin/env bash
set -u

export PATH="/opt/hudvenv/bin:/usr/local/bin:/usr/bin:/bin:${PATH:-}"
export HOME="${HOME:-/root}"

REPO=${REPO_DIR:-$PWD}
G=${GRADER_DIR:-/hud/grader}
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
if [ ! -d "$G/tests" ]; then
  G="$SCRIPT_DIR"
fi
LOGDIR=${GRADER_STATE_DIR:-/hud/logs/grading-state}
if ! mkdir -p "$LOGDIR" 2>/dev/null; then
  LOGDIR="${TMPDIR:-/tmp}/hud-grading-state"
  mkdir -p "$LOGDIR"
fi

if [ -z "${PYTHON_BIN:-}" ] && [ -x /opt/hudvenv/bin/python3 ]; then
  PYTHON_BIN=/opt/hudvenv/bin/python3
fi
PYTHON_BIN=${PYTHON_BIN:-python3}
export PYTHONPATH="$REPO/lib${PYTHONPATH:+:$PYTHONPATH}"

detail() {
  echo "  ----- $1 (last 2000 bytes) -----"
  tail -c 2000 "$2" 2>/dev/null | sed 's/^/  | /'
  echo "  -----"
}

run_python_test() {
  local test_file="$1"
  local log="$LOGDIR/$(basename "$test_file").log"
  (cd "$REPO" && "$PYTHON_BIN" "$G/tests/$test_file") >"$log" 2>&1
  local rc=$?
  [ $rc -ne 0 ] && detail "$test_file" "$log"
  return $rc
}

criterion_json_null_equality() {
  run_python_test json_null_equality.py
}

criterion_json_null_inequality() {
  run_python_test json_null_inequality.py
}

criterion_nested_path_support() {
  run_python_test nested_path_support.py
}

criterion_membership_support() {
  run_python_test membership_support.py
}

criterion_reverse_operand_support() {
  run_python_test reverse_operand_support.py
}

criterion_is_operator_support() {
  run_python_test is_operator_support.py
}

criterion_mixed_membership_support() {
  run_python_test mixed_membership_support.py
}

criterion_scalar_cache_stability() {
  run_python_test scalar_cache_stability.py
}

criterion_membership_cache_stability() {
  run_python_test membership_cache_stability.py
}

criterion_distinct_predicate_support() {
  run_python_test distinct_predicate_support.py
}

criterion_cross_shape_cache_stability() {
  run_python_test cross_shape_cache_stability.py
}

criterion_compiled_sql_shape() {
  run_python_test compiled_sql_shape.py
}

criterion_regression_backcompat() {
  run_python_test regression_backcompat.py
}

criterion_test_quality() {
  run_python_test test_quality.py
}

criterion_maintainer_review() {
  run_python_test maintainer_review.py
}

CRITERIA="json_null_equality json_null_inequality nested_path_support membership_support reverse_operand_support is_operator_support mixed_membership_support scalar_cache_stability membership_cache_stability distinct_predicate_support cross_shape_cache_stability compiled_sql_shape regression_backcompat test_quality maintainer_review"

name="${1:-}"
case " $CRITERIA " in
  *" $name "*)
    if "criterion_$name"; then
      echo "CRITERION $name: PASS"
      exit 0
    else
      echo "CRITERION $name: FAIL"
      exit 1
    fi
    ;;
  *)
    echo "usage: run_grading.sh <criterion>; one of: $CRITERIA" >&2
    exit 2
    ;;
esac
