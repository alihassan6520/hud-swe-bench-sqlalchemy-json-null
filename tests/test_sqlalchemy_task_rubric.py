import tasks


def test_sqlalchemy_json_null_rubric_weights_are_balanced():
    total = sum(weight for _name, weight, _blocker, _kind, _timeout in tasks.GRADERS)
    blocker_total = sum(
        weight for _name, weight, blocker, _kind, _timeout in tasks.GRADERS if blocker
    )
    quality_total = sum(
        weight for name, weight, _blocker, _kind, _timeout in tasks.GRADERS
        if name in {"test_quality", "maintainer_review"}
    )

    assert round(total, 2) == 1.0
    assert round(blocker_total, 2) == 0.90
    assert blocker_total < tasks.BLOCKER_CAP
    assert round(quality_total, 2) == 0.06
