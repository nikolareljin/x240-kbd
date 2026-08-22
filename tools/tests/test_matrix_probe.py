import pytest
import matrix_probe as mp


def test_pass_maps_cover_all_40_pads_with_overlap():
    a = mp.build_pad_map(mp.pass_pads("A"))
    b = mp.build_pad_map(mp.pass_pads("B"))
    assert set(a) | set(b) == set(range(1, 41))
    assert set(a) & set(b) == set(range(15, 27))
    assert len(a) == len(b) == 26
    assert a[1] == "GP0" and b[15] == "GP0" and b[40] == "GP28"


def test_build_pad_map_refuses_more_pads_than_gpio():
    with pytest.raises(ValueError):
        mp.build_pad_map(tuple(range(1, 28)))


def test_pass_pads_rejects_unknown():
    with pytest.raises(ValueError):
        mp.pass_pads("C")


def test_group_pairs_and_summary():
    results = {"A": (3, 10), "S": (3, 11), "Q": (5, 10)}
    drive, sense = mp.group_pairs(results)
    assert drive == [3, 5] and sense == [10, 11]
    assert "2 x 2" in mp.format_summary(results)


def test_merge_results_detects_conflicts():
    a = {"A": (3, 10), "S": (3, 11)}
    b = {"S": (3, 11), "Z": (7, 10), "A": (4, 10)}
    merged, conflicts = mp.merge_results(a, b)
    assert merged["Z"] == (7, 10) and merged["S"] == (3, 11)
    assert conflicts == [("A", (3, 10), (4, 10))]


def test_format_table_is_markdown_sorted_by_pads():
    table = mp.format_table({"B": (5, 10), "A": (3, 12)}, "A")
    lines = table.splitlines()
    assert lines[0].startswith("| Key |")
    assert lines[2] == "| A | 3 | 12 | A |"
    assert lines[3] == "| B | 5 | 10 | A |"


def test_hardware_not_imported_on_host():
    assert mp.ON_DEVICE is False
