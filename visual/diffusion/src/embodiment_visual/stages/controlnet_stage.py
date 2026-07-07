"""Conditioning ControlNet a partir dels render passes (depth + normal).

Requereix `diffusers` (no instal·lat en aquesta màquina de desenvolupament —
import diferit perquè el mòdul es pugui importar/testejar sense la llibreria).
"""
from __future__ import annotations

from dataclasses import dataclass

from PIL import Image

from ..config import ControlNetConfig
from ..gbuffer import GBufferFrame


@dataclass
class ControlNetConditioning:
    config: ControlNetConfig
    _pipe_controlnets: list = None
    _loaded: bool = False

    def load(self) -> None:
        """Carrega els pesos ControlNet (depth i, opcionalment, normal). Pesat: no cridar
        en aquesta màquina, només al node d'inferència (Strix Halo)."""
        from diffusers import ControlNetModel  # noqa: PLC0415

        controlnets = [ControlNetModel.from_pretrained(self.config.model_id)]
        if self.config.use_normal:
            controlnets.append(ControlNetModel.from_pretrained(self.config.normal_model_id))
        self._pipe_controlnets = controlnets
        self._loaded = True

    def conditioning_images(self, frame: GBufferFrame) -> list[Image.Image]:
        """Converteix els passes crus del motor a les imatges que ControlNet espera.

        El depth pass del motor (engine/shaders/depth_capture.gdshader) ja és
        gris normalitzat [0,1]; el normal pass ja és RGB (n*0.5+0.5) — cap
        preprocessador addicional (com controlnet_aux) hauria de caldre.
        """
        images = [Image.fromarray(frame.depth)]
        if self.config.use_normal:
            images.append(Image.fromarray(frame.normal))
        return images

    def conditioning_scales(self) -> list[float]:
        scales = [self.config.conditioning_scale]
        if self.config.use_normal:
            scales.append(self.config.conditioning_scale)
        return scales
