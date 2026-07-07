"""Carrega els render passes exportats pel motor (engine/scripts/gbuffer_export.gd):
color_%04d.png, depth_%04d.png, normal_%04d.png, motion_%04d.png dins un directori.

Motion vectors: el motor els codifica com a color (R=dx,G=dy en espai UV, amb
bias+scale a l'estil normal map) perquè es puguin desar com a PNG — vegeu
engine/shaders/motion_capture.gdshader. `_decode_motion` desfà aquesta
codificació i retorna dx,dy en PÍXELS, el format que `warp.warp_frame` espera.
`MOTION_SCALE` ha de coincidir EXACTAMENT amb la constant del mateix nom al shader.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

MOTION_SCALE = 0.25


@dataclass
class GBufferFrame:
    index: int
    color: np.ndarray
    depth: np.ndarray
    normal: np.ndarray
    motion: np.ndarray | None = None


def _load_png(path: Path) -> np.ndarray:
    return np.array(Image.open(path).convert("RGB"))


def decode_motion(encoded: np.ndarray) -> np.ndarray:
    """Desfà la codificació del shader: color [0,255] -> motion en píxels (H,W,2).

    Godot fa servir NDC amb Y amunt; una imatge normalment té la fila 0 a dalt
    (Y avall), per això s'inverteix el signe de dy en decodificar.
    """
    h, w = encoded.shape[:2]
    normalized = encoded[..., :2].astype(np.float32) / 255.0
    motion_uv = (normalized * 2.0 - 1.0) * MOTION_SCALE
    dx = motion_uv[..., 0] * w
    dy = -motion_uv[..., 1] * h
    return np.stack([dx, dy], axis=-1)


def encode_motion(motion_px: np.ndarray, width: int, height: int) -> np.ndarray:
    """Inversa de `decode_motion` — útil per generar PNGs sintètics als tests.

    Retorna (H,W,3) com el shader real (ALBEDO = vec3(encoded_dx, encoded_dy, 0.5)).
    """
    dx = motion_px[..., 0] / width
    dy = -motion_px[..., 1] / height
    motion_uv = np.stack([dx, dy], axis=-1)
    encoded_rg = np.clip(motion_uv / MOTION_SCALE, -1.0, 1.0) * 0.5 + 0.5
    h, w = motion_px.shape[:2]
    blue = np.full((h, w, 1), 0.5)
    encoded = np.concatenate([encoded_rg, blue], axis=-1)
    return np.clip(encoded * 255.0, 0, 255).astype(np.uint8)


def load_frame(frame_dir: Path | str, index: int) -> GBufferFrame:
    frame_dir = Path(frame_dir)
    color_path = frame_dir / f"color_{index:04d}.png"
    depth_path = frame_dir / f"depth_{index:04d}.png"
    normal_path = frame_dir / f"normal_{index:04d}.png"
    motion_path = frame_dir / f"motion_{index:04d}.png"

    for required in (color_path, depth_path, normal_path):
        if not required.exists():
            raise FileNotFoundError(f"Falta {required} — has executat gbuffer_export.gd (tecla P)?")

    motion = decode_motion(_load_png(motion_path)) if motion_path.exists() else None

    return GBufferFrame(
        index=index,
        color=_load_png(color_path),
        depth=_load_png(depth_path),
        normal=_load_png(normal_path),
        motion=motion,
    )


def iter_frames(frame_dir: Path | str):
    """Itera tots els frames disponibles a `frame_dir` en ordre d'índex."""
    frame_dir = Path(frame_dir)
    indices = sorted(
        int(p.stem.split("_")[1])
        for p in frame_dir.glob("color_*.png")
    )
    for idx in indices:
        yield load_frame(frame_dir, idx)
