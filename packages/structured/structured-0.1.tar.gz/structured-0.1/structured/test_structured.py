from nose.tools import assert_equals

from structured.analyzer import getter_tree
from structured.finder import lookup, filtered_lookup

from .test_datasamples import SAMPLE1, SAMPLE2, SAMPLE3, SAMPLE4


def test_plain():
    simple_path = "level1_1.level2_1.level3"
    getters = getter_tree(SAMPLE1, simple_path)

    assert len(getters) == 3
    assert lookup(*getters)(SAMPLE1) == SAMPLE1["level1_1"]["level2_1"]["level3"]


def test_array():
    path = "level1_1.level2_1[].level3"
    getters = getter_tree(SAMPLE2, path)

    assert len(getters) == 3
    assert lookup(*getters)(SAMPLE2) == ["value1", "value2", "value3"]


def test_array_with_tree():
    path = "level1_1.level2_1[].level3.data"
    getters = getter_tree(SAMPLE3, path)

    assert len(getters) == 4
    assert lookup(*getters)(SAMPLE3) == ["value1", "value2", "value3"]


def test_subarrays():
    path = "level1_1.level2_1[].level3[].data"
    getters = getter_tree(SAMPLE4, path)

    assert lookup(*getters)(SAMPLE4) == [
        ["value1", "value2"], ["value3", "value4"], ["value5", "value6"]]


def test_filters_merge():
    path = "level1_1.level2_1[].level3[].data|merge"

    assert_equals(
        filtered_lookup(SAMPLE4, path),
        ["value1", "value2", "value3", "value4", "value5", "value6"]
    )

    path = "level1_1.level2_1[].level3[].data|merge|join:s=,"
    assert_equals(
        filtered_lookup(SAMPLE4, path),
        ",".join(["value1", "value2", "value3", "value4", "value5", "value6"])
    )

    path = "level1_1.level2_1[].level3[].data|merge|last"
    assert_equals(
        filtered_lookup(SAMPLE4, path),
        "value6"
    )

    path = "level1_1.level2_1[].level3[].data|last"
    assert_equals(
        filtered_lookup(SAMPLE4, path),
        ["value5", "value6"]
    )
