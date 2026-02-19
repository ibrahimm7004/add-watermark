import pytest

from watermarker.engine import ValidationError, opacity_to_alpha


def test_opacity_to_alpha_endpoints() -> None:
    assert opacity_to_alpha(0) == 0
    assert opacity_to_alpha(100) == 255


def test_opacity_to_alpha_midpoint() -> None:
    assert opacity_to_alpha(50) == 128


@pytest.mark.parametrize("value", [-1, 101])
def test_opacity_to_alpha_rejects_out_of_range(value: int) -> None:
    with pytest.raises(ValidationError):
        opacity_to_alpha(value)
