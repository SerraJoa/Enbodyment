import numpy as np
import pytest

from embodiment_visual.config import InterpolationConfig
from embodiment_visual.interpolate import FrameInterpolator


def test_frames_between_computes_ratio():
    interp = FrameInterpolator(config=InterpolationConfig(target_fps=30, keyframe_fps=12))
    assert interp.frames_between() == 1  # 30/12 = 2.5 -> round 2 -> 1 intermedi


def test_interpolate_blend_without_motion():
    interp = FrameInterpolator(config=InterpolationConfig(method="blur_fallback"))
    a = np.zeros((4, 4, 3), dtype=np.uint8)
    b = np.full((4, 4, 3), 255, dtype=np.uint8)

    mid = interp.interpolate(a, b, 0.5)

    assert int(mid[0, 0, 0]) == pytest.approx(127, abs=2)


def test_interpolate_rife_warns_and_falls_back():
    interp = FrameInterpolator(config=InterpolationConfig(method="rife"))
    a = np.zeros((4, 4, 3), dtype=np.uint8)
    b = np.full((4, 4, 3), 255, dtype=np.uint8)

    with pytest.warns(RuntimeWarning):
        mid = interp.interpolate(a, b, 0.5)

    assert mid.shape == (4, 4, 3)
