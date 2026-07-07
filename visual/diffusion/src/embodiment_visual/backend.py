"""Selecció de dispositiu/backend segons maquinari disponible.

A l'Strix Halo (objectiu real) no hi ha TensorRT ni CUDA: és ROCm/ONNX.
A la màquina de desenvolupament actual (Ryzen 8500G + iGPU feble, torch
compilat només per CPU) el pipeline sencer NO és viable — aquest mòdul
serveix per detectar-ho i fallar de forma clara enlloc de penjar-se intentant
carregar models a una GPU que no hi és.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BackendInfo:
    name: str  # "cuda" | "rocm" | "directml" | "cpu"
    device_str: str  # el que es passa a torch.device(...)
    is_gpu: bool


def _torch():
    import torch  # import diferit: no volem que important aquest mòdul requereixi torch instal·lat

    return torch


def detect_available_backends() -> list[BackendInfo]:
    """Detecta backends disponibles en aquesta màquina. No assumeix cap GPU present."""
    torch = _torch()
    backends: list[BackendInfo] = []

    if torch.cuda.is_available():
        # torch.cuda també cobreix builds ROCm (HIP s'exposa via la mateixa API cuda.*)
        is_rocm = getattr(torch.version, "hip", None) is not None
        backends.append(BackendInfo(name="rocm" if is_rocm else "cuda", device_str="cuda", is_gpu=True))

    try:
        import torch_directml  # noqa: F401

        backends.append(BackendInfo(name="directml", device_str="privateuseone", is_gpu=True))
    except ImportError:
        pass

    backends.append(BackendInfo(name="cpu", device_str="cpu", is_gpu=False))
    return backends


def select_backend(preference: list[str] | None = None) -> BackendInfo:
    """Tria el primer backend disponible segons l'ordre de preferència.

    `preference` és una llista de noms ("cuda", "rocm", "directml", "cpu");
    per defecte ve de PipelineConfig.backend.device_preference.
    """
    available = detect_available_backends()
    by_name = {b.name: b for b in available}

    order = preference or ["cuda", "rocm", "directml", "cpu"]
    for name in order:
        if name in by_name:
            return by_name[name]

    return by_name["cpu"]  # sempre hi és


def warn_if_underpowered(backend: BackendInfo) -> None:
    if not backend.is_gpu:
        import warnings

        warnings.warn(
            "Cap GPU disponible: el pipeline de difusió en temps real NO és viable en "
            "aquest backend (CPU). Útil només per provar la lògica del pipeline amb "
            "models petits/mock, no per inferència real. Objectiu real: Strix Halo (ROCm).",
            RuntimeWarning,
            stacklevel=2,
        )
