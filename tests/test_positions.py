from watermarker.engine import compute_position


def test_compute_position_tl_respects_margin() -> None:
    assert compute_position((200, 100), (40, 20), "tl", margin=24) == (24, 24)


def test_compute_position_tr_respects_margin() -> None:
    assert compute_position((200, 100), (40, 20), "tr", margin=24) == (136, 24)


def test_compute_position_bl_respects_margin() -> None:
    assert compute_position((200, 100), (40, 20), "bl", margin=24) == (24, 56)


def test_compute_position_br_respects_margin() -> None:
    assert compute_position((200, 100), (40, 20), "br", margin=24) == (136, 56)


def test_compute_position_center() -> None:
    assert compute_position((200, 100), (40, 20), "c", margin=24) == (80, 40)
