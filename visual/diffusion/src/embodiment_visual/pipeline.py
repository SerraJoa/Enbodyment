"""Orquestració del pipeline sencer (architecture.md §5):
ControlNet + IP-Adapter + LCM + StreamDiffusion (latent recycling) + warp per
motion vectors + interpolació piramidal.

Aquest mòdul defineix el FLUX; les crides pesades (`.load()`, generació real)
no s'han pogut executar en aquesta màquina (CPU-only, sense diffusers
instal·lat). Vegeu backend.py — `select_backend()` + `warn_if_underpowered()`
avisen clarament si s'intenta córrer sense GPU útil.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .backend import select_backend, warn_if_underpowered
from .config import PipelineConfig
from .gbuffer import GBufferFrame
from .interpolate import FrameInterpolator
from .stages.controlnet_stage import ControlNetConditioning
from .stages.identity_stage import IdentityAdapter
from .stages.stream import LatentRecycler
from .warp import warp_frame


@dataclass
class VisualPipeline:
    config: PipelineConfig
    _controlnet: ControlNetConditioning = field(init=False)
    _identity: IdentityAdapter = field(init=False)
    _recycler: LatentRecycler = field(init=False)
    _interpolator: FrameInterpolator = field(init=False)
    _base_pipe = None

    def __post_init__(self) -> None:
        self._controlnet = ControlNetConditioning(config=self.config.controlnet)
        self._identity = IdentityAdapter(config=self.config.identity)
        self._recycler = LatentRecycler(config=self.config.stream)
        self._interpolator = FrameInterpolator(config=self.config.interpolation)

    def load(self) -> None:
        """Carrega tots els pesos. NOMÉS cridar en un node amb GPU (Strix Halo)."""
        backend = select_backend(self.config.backend.device_preference)
        warn_if_underpowered(backend)

        self._controlnet.load()
        if self.config.identity.enabled:
            self._identity.load()
        # TODO: carregar base_model_id + adjuntar controlnets + scheduler.build_scheduler(...)
        raise NotImplementedError(
            "Càrrega del pipeline base de diffusers pendent — connectar quan hi hagi "
            "GPU real per provar-ho (aquesta màquina és CPU-only)."
        )

    def run_keyframe(self, frame: GBufferFrame):
        """Genera un keyframe complet (denoise real amb ControlNet + identitat)."""
        if self._base_pipe is None:
            raise RuntimeError("Crida .load() abans de generar frames.")
        raise NotImplementedError("Pendent de connectar amb el pipeline real de diffusers.")

    def run_recycled(self, frame: GBufferFrame, previous_color) -> "object":
        """Warp del frame anterior segons motion vectors + denoise parcial (latent recycling).

        Si `frame.motion` és None (el motor encara no exporta motion vectors —
        veure engine/README.md), cau a `run_keyframe` sencer.
        """
        if frame.motion is None:
            return self.run_keyframe(frame)

        warped = warp_frame(previous_color, frame.motion)
        raise NotImplementedError(
            "Warp fet; falta el pas de denoise parcial sobre `warped` amb LatentRecycler "
            "(pendent de connectar amb el pipeline real de diffusers)."
        )
