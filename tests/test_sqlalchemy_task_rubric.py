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

    assert total == 1.0
    assert blocker_total == 0.55
    assert blocker_total < tasks.BLOCKER_CAP
    assert quality_total == 0.40
