"""Scheduler LCM (Latent Consistency Model) per reduir passos de denoise —
part de "LCM/destil·lació de passos" a architecture.md §5.
"""
from __future__ import annotations

from ..config import SchedulerConfig


def build_scheduler(config: SchedulerConfig, pipe):
    """Substitueix l'scheduler del pipeline de diffusers per LCM (o el que toqui).

    `pipe` és un pipeline de `diffusers` ja carregat — import diferit perquè
    aquest mòdul no requereixi `diffusers` instal·lat només per importar-lo.
    """
    if config.type == "lcm":
        from diffusers import LCMScheduler  # noqa: PLC0415

        pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)
        return pipe.scheduler

    raise ValueError(f"Scheduler '{config.type}' no suportat (només 'lcm' de moment).")
