"""Latent recycling a l'estil StreamDiffusion: inicialitza el denoise del frame
actual a partir del latent del frame anterior (no de soroll pur), amb un
denoise_strength baix — és el que fa viable el "temps real tou" (architecture.md §5).

La gestió d'estat (aquest mòdul) és pura àlgebra de tensors i es pot provar
sense cap model carregat; la crida real al pipeline de diffusers és a pipeline.py.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..config import StreamConfig


@dataclass
class LatentRecycler:
    config: StreamConfig
    _previous_latents = None  # torch.Tensor | None, sense type hint per no importar torch al top-level

    def reset(self) -> None:
        self._previous_latents = None

    def has_previous(self) -> bool:
        return self._previous_latents is not None

    def init_latents(self, fresh_noise):
        """Combina el latent anterior amb soroll fresc segons denoise_strength.

        strength=0 -> reutilitza el latent anterior tal qual (cap canvi).
        strength=1 -> soroll pur (equivalent a generar el frame des de zero).
        """
        import torch  # noqa: PLC0415

        if not self.config.latent_recycling or self._previous_latents is None:
            return fresh_noise

        strength = self.config.denoise_strength
        if not 0.0 <= strength <= 1.0:
            raise ValueError(f"denoise_strength ha de ser [0,1], rebut {strength}")

        alpha = torch.sqrt(torch.tensor(1.0 - strength))
        beta = torch.sqrt(torch.tensor(strength))
        return alpha * self._previous_latents + beta * fresh_noise

    def update(self, new_latents) -> None:
        self._previous_latents = new_latents.detach().clone()
