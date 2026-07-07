"""Interpolació piramidal: keyframe (difusió real) + RIFE + blur segons
magnitud de moviment (architecture.md §5). Genera els frames intermedis entre
keyframes sense tornar a passar per difusió.
"""
from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from .config import InterpolationConfig
from .warp import motion_magnitude


@dataclass
class FrameInterpolator:
    config: InterpolationConfig

    def frames_between(self) -> int:
        """Quants frames intermedis calen entre dos keyframes segons els fps objectiu."""
        if self.config.keyframe_fps <= 0:
            return 0
        ratio = self.config.target_fps / self.config.keyframe_fps
        return max(0, round(ratio) - 1)

    def interpolate(self, frame_a: np.ndarray, frame_b: np.ndarray, t: float, motion_vectors: np.ndarray | None = None) -> np.ndarray:
        """Interpola entre dos keyframes a t in (0,1).

        `method="rife"` hauria de cridar un model RIFE real (pendent — no s'ha
        pogut provar sense el checkpoint ni GPU). De moment sempre fa servir
        el fallback: blend lineal + blur proporcional a la magnitud de
        moviment, que és honest sobre el que fa (no és RIFE de veritat).
        """
        if self.config.method == "rife":
            import warnings

            warnings.warn(
                "FrameInterpolator: mètode 'rife' configurat però no implementat "
                "(pendent de connectar el model). Usant blur_fallback.",
                RuntimeWarning,
                stacklevel=2,
            )
        return self._blur_fallback(frame_a, frame_b, t, motion_vectors)

    def _blur_fallback(self, frame_a: np.ndarray, frame_b: np.ndarray, t: float, motion_vectors: np.ndarray | None) -> np.ndarray:
        blended = cv2.addWeighted(frame_a, 1.0 - t, frame_b, t, 0.0)

        if motion_vectors is None:
            return blended

        magnitude = motion_magnitude(motion_vectors)
        max_mag = float(magnitude.max()) if magnitude.size else 0.0
        if max_mag <= 1e-6:
            return blended

        # Kernel de blur proporcional a la magnitud mitjana (aproximació barata:
        # un sol kernel global, no per-píxel, suficient per validar la idea).
        avg_mag = float(magnitude.mean())
        kernel_size = max(1, int(avg_mag * self.config.motion_blur_scale))
        if kernel_size % 2 == 0:
            kernel_size += 1
        if kernel_size <= 1:
            return blended

        return cv2.GaussianBlur(blended, (kernel_size, kernel_size), 0)
