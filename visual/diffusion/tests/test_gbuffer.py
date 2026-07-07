from pathlib import Path

import numpy as np
from PIL import Image

from embodiment_visual.gbuffer import decode_motion, encode_motion, iter_frames, load_frame


def _write_png(path: Path, color: tuple[int, int, int]):
    img = Image.new("RGB", (8, 8), color)
    img.save(path)


def test_load_frame_reads_color_depth_normal(tmp_path: Path):
    _write_png(tmp_path / "color_0000.png", (10, 20, 30))
    _write_png(tmp_path / "depth_0000.png", (128, 128, 128))
    _write_png(tmp_path / "normal_0000.png", (127, 127, 255))

    frame = load_frame(tmp_path, 0)

    assert frame.index == 0
    assert frame.color.shape == (8, 8, 3)
    assert frame.motion is None
    assert tuple(frame.color[0, 0]) == (10, 20, 30)


def test_load_frame_missing_raises(tmp_path: Path):
    try:
        load_frame(tmp_path, 0)
        assert False, "hauria d'haver llançat FileNotFoundError"
    except FileNotFoundError:
        pass


def test_iter_frames_orders_by_index(tmp_path: Path):
    for idx in (2, 0, 1):
        for kind in ("color", "depth", "normal"):
            _write_png(tmp_path / f"{kind}_{idx:04d}.png", (idx, idx, idx))

    indices = [f.index for f in iter_frames(tmp_path)]

    assert indices == [0, 1, 2]


def test_motion_encode_decode_roundtrip():
    width, height = 64, 32
    motion_px = np.zeros((height, width, 2), dtype=np.float32)
    motion_px[..., 0] = 3.0   # dx
    motion_px[..., 1] = -2.0  # dy

    encoded = encode_motion(motion_px, width, height)
    decoded = decode_motion(encoded)

    # Arrodoniment a uint8 (255 valors) introdueix quantització; tolerància petita n'hi ha prou.
    assert np.allclose(decoded[..., 0], 3.0, atol=0.2)
    assert np.allclose(decoded[..., 1], -2.0, atol=0.2)


def test_motion_encode_zero_motion_is_neutral_gray():
    motion_px = np.zeros((4, 4, 2), dtype=np.float32)
    encoded = encode_motion(motion_px, 4, 4)
    assert np.all(encoded == 127) or np.all(encoded == 128)


def test_load_frame_decodes_motion_when_present(tmp_path: Path):
    _write_png(tmp_path / "color_0000.png", (10, 20, 30))
    _write_png(tmp_path / "depth_0000.png", (128, 128, 128))
    _write_png(tmp_path / "normal_0000.png", (127, 127, 255))

    # dx ha d'estar dins el marge codificable: +/- MOTION_SCALE * width = +/- 2px per width=8.
    motion_px = np.zeros((8, 8, 2), dtype=np.float32)
    motion_px[..., 0] = 1.0
    encoded = encode_motion(motion_px, 8, 8)
    Image.fromarray(encoded).save(tmp_path / "motion_0000.png")

    frame = load_frame(tmp_path, 0)

    assert frame.motion is not None
    assert np.allclose(frame.motion[..., 0], 1.0, atol=0.1)
