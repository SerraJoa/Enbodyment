"""Warp d'un frame segons motion vectors ground-truth del motor.

Idea (architecture.md §5): repintar només el que canvia. Enlloc de re-denoise
sencer a cada frame, es desplaça (warp) el frame anterior segons el flux de
moviment real que el motor ja coneix (no cal estimar-lo per optical flow), i
només la diferència es torna a passar per difusió.
"""
from __future__ import annotations

import numpy as np


def warp_frame(frame: np.ndarray, motion_vectors: np.ndarray) -> np.ndarray:
    """Desplaça `frame` (H,W,C) segons `motion_vectors` (H,W,2) en píxels (dx,dy).

    `motion_vectors[y, x] = (dx, dy)` indica d'on ve el píxel (y,x) al frame
    anterior — conveni "backward warp", el mateix que fa servir cv2.remap.
    """
    import cv2

    h, w = frame.shape[:2]
    if motion_vectors.shape[:2] != (h, w):
        raise ValueError(f"motion_vectors shape {motion_vectors.shape[:2]} != frame shape {(h, w)}")

    grid_x, grid_y = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    map_x = grid_x + motion_vectors[..., 0].astype(np.float32)
    map_y = grid_y + motion_vectors[..., 1].astype(np.float32)

    return cv2.remap(frame, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


def occlusion_mask(motion_vectors: np.ndarray, threshold: float = 1.5) -> np.ndarray:
    """Marca com a 'desoclusió' (True = cal repintar de nou) els píxels on el
    warp probablement falla: divergència alta del camp de motion vectors.

    Aproximació barata sense z-buffer: mira la divergència local del camp.
    Quan hi hagi el z-buffer de desoclusions (arquitectura §5), substituir per
    la comparació de profunditat real.
    """
    dx = motion_vectors[..., 0]
    dy = motion_vectors[..., 1]
    grad_dx_x = np.gradient(dx, axis=1)
    grad_dy_y = np.gradient(dy, axis=0)
    divergence = np.abs(grad_dx_x) + np.abs(grad_dy_y)
    return divergence > threshold


def motion_magnitude(motion_vectors: np.ndarray) -> np.ndarray:
    """Magnitud (H,W) del camp de motion vectors — es fa servir per graduar
    el blur a la interpolació piramidal (interpolate.py)."""
    return np.sqrt(motion_vectors[..., 0] ** 2 + motion_vectors[..., 1] ** 2)
