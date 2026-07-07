import numpy as np

from embodiment_visual.warp import motion_magnitude, occlusion_mask, warp_frame


def test_warp_zero_motion_is_identity():
    frame = np.random.randint(0, 255, (16, 16, 3), dtype=np.uint8)
    motion = np.zeros((16, 16, 2), dtype=np.float32)

    warped = warp_frame(frame, motion)

    assert np.array_equal(warped, frame)


def test_warp_shifts_content():
    frame = np.zeros((10, 10, 3), dtype=np.uint8)
    frame[5, 5] = [255, 255, 255]  # un sol píxel blanc a (x=5, y=5)

    motion = np.zeros((10, 10, 2), dtype=np.float32)
    # volem que el píxel de sortida (x=6,y=5) llegeixi de (x=5,y=5) -> dx=-1
    motion[5, 6] = [-1.0, 0.0]

    warped = warp_frame(frame, motion)

    assert warped[5, 6].tolist() == [255, 255, 255]


def test_warp_rejects_mismatched_shape():
    frame = np.zeros((10, 10, 3), dtype=np.uint8)
    motion = np.zeros((5, 5, 2), dtype=np.float32)
    try:
        warp_frame(frame, motion)
        assert False, "hauria d'haver llançat ValueError"
    except ValueError:
        pass


def test_motion_magnitude():
    motion = np.zeros((2, 2, 2), dtype=np.float32)
    motion[0, 0] = [3.0, 4.0]  # magnitud 5
    mag = motion_magnitude(motion)
    assert abs(mag[0, 0] - 5.0) < 1e-6
    assert mag[1, 1] == 0.0


def test_occlusion_mask_flags_high_divergence():
    motion = np.zeros((20, 20, 2), dtype=np.float32)
    # camp amb divergencia forta al mig (font/escampament)
    for y in range(20):
        for x in range(20):
            motion[y, x] = [x - 10, y - 10]

    mask = occlusion_mask(motion, threshold=0.5)

    assert mask.any()
