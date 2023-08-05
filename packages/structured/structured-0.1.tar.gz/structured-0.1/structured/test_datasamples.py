SAMPLE1 = {
    "level1_0": None,
    "level1_1": {
        "level2_1": {
            "level3": "value1"
        },
        "level2_2": {
        }
    }
}

SAMPLE2 = {
    "level1_0": None,
    "level1_1": {
        "level2_1": [
            {"level3": "value1"},
            {"level3": "value2"},
            {"level3": "value3"}
        ],
        "level2_2": {
        }
    }
}


SAMPLE3 = {
    "level1_0": None,
    "level1_1": {
        "level2_1": [
            {"level3": {"data": "value1"}},
            {"level3": {"data": "value2"}},
            {"level3": {"data": "value3"}}
        ],
        "level2_2": {
        }
    }
}


SAMPLE4 = {
    "level1_1": {
        "level2_1": [
            {"level3": [{"data": "value1"}, {"data": "value2"}]},
            {"level3": [{"data": "value3"}, {"data": "value4"}]},
            {"level3": [{"data": "value5"}, {"data": "value6"}]}
        ]
    }
}
