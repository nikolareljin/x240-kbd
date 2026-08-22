import shift_register_test as sr


def test_all_high_when_nothing_grounded():
    levels = sr.decode_chain(bytes([0xFF, 0xFF, 0xFF]))
    assert len(levels) == 24 and all(levels)
    assert sr.low_lines(levels) == []


def test_bit_positions_map_to_sense_lines():
    # U1.D0 = S0 is bit 0 of byte 0; U3.D7 = S23 is bit 7 of byte 2
    assert sr.low_lines(sr.decode_chain(bytes([0xFE, 0xFF, 0xFF]))) == [0]
    assert sr.low_lines(sr.decode_chain(bytes([0xFF, 0xFF, 0x7F]))) == [23]
    assert sr.low_lines(sr.decode_chain(bytes([0xFF, 0xEF, 0xFF]))) == [12]


def test_pattern_prints_s23_left_to_s0_right():
    p = sr.pattern(sr.decode_chain(bytes([0xFE, 0xFF, 0x7F])))
    assert p == "U3:01111111  U2:11111111  U1:11111110"


def test_diagnose_explains_common_wiring_faults():
    assert "not wired" in sr.diagnose(4, [])
    assert "shorted" in sr.diagnose(4, [4, 5])
    assert "chip order" in sr.diagnose(4, [12])
    assert "reverse" in sr.diagnose(1, [6])
    assert "swapped" in sr.diagnose(1, [2])


def test_hardware_not_imported_on_host():
    assert sr.ON_DEVICE is False
