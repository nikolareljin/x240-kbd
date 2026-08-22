import ps2_sniffer as ps


def test_odd_parity():
    assert ps.odd_parity(0x00) == 1
    assert ps.odd_parity(0x01) == 0
    assert ps.odd_parity(0xFF) == 1
    assert ps.odd_parity(0xF4) == 0   # 0b11110100 -> five ones -> parity 0


def test_special_sequence_spells_argument_msb_pair_first():
    assert ps.special_sequence(0xC1) == [0xE8, 3, 0xE8, 0, 0xE8, 0, 0xE8, 1]
    assert ps.special_sequence(0x00) == [0xE8, 0] * 4


def test_decode_relative_signs_and_buttons():
    assert ps.decode_relative(0x08, 5, 3) == (5, 3, False, False, False)
    assert ps.decode_relative(0x08 | 0x10 | 0x20 | 0x01, 0xFE, 0xFF) == (-2, -1, True, False, False)
    assert ps.relative_packet_valid(0x08) and not ps.relative_packet_valid(0x00)


def _abs(w, x, y, z, left=0, right=0):
    """Build a valid 6-byte Synaptics absolute packet for a given W, X, Y, Z."""
    b0 = 0x80 | ((w & 0x0C) << 2) | ((w & 0x02) << 1) | (right << 1) | left
    b3 = 0xC0 | ((x >> 8) & 0x10) | ((y >> 7) & 0x20) | ((w & 0x01) << 2)
    b1 = ((y >> 4) & 0xF0) | ((x >> 8) & 0x0F)
    return [b0, b1, z, b3, x & 0xFF, y & 0xFF]


def test_abs_packet_framing():
    assert ps.abs_packet_valid(_abs(4, 3000, 2500, 40))
    assert not ps.abs_packet_valid([0x00] * 6)
    assert not ps.abs_packet_valid(_abs(4, 1, 1, 1)[:5])


def test_decode_absolute_touch_round_trips_coordinates():
    for w, x, y, z in [(4, 3000, 2500, 40), (5, 0x1FFF, 0x1FFF, 255), (0, 1, 1, 1)]:
        pkt = ps.decode_absolute(_abs(w, x, y, z, left=1))
        assert pkt["kind"] == "touch"
        assert (pkt["w"], pkt["x"], pkt["y"], pkt["z"], pkt["left"]) == (w, x, y, z, True)


def test_decode_absolute_guest_frame_carries_embedded_ps2_packet():
    raw = _abs(3, 0, 0, 0)
    raw[1], raw[4], raw[5] = 0x08 | 0x10, 0xFD, 0x07      # guest: dx=-3, dy=+7
    pkt = ps.decode_absolute(raw)
    assert pkt["kind"] == "guest" and pkt["w"] == 3
    assert ps.decode_relative(*pkt["guest"])[:2] == (-3, 7)


def test_capabilities_bits_match_linux_layout():
    caps = ps.capabilities(0x80, 0x00, 0x80)
    assert caps["extended"] and caps["pass_through"]
    assert not ps.capabilities(0x00, 0x00, 0x00)["pass_through"]


def test_verdict_is_unambiguous():
    assert "PASS-THROUGH FRAMES SEEN" in ps.verdict(5, 40, True, 20)
    assert "capability bit is CLEAR" in ps.verdict(0, 40, False, 20)
    assert "capability bit is SET" in ps.verdict(0, 40, True, 20)


def test_hardware_not_imported_on_host():
    assert ps.ON_DEVICE is False
