"""Configuració del pipeline de difusió, carregada des d'un YAML.

Un sol fitxer de config descriu totes les etapes (§5 de docs/architecture.md):
ControlNet, identitat (IP-Adapter), scheduler LCM, streaming amb latent
recycling, i interpolació piramidal.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class ControlNetConfig:
    model_id: str = "lllyasviel/control_v11f1p_sd15_depth"
    conditioning_scale: float = 1.0
    use_normal: bool = True
    normal_model_id: str = "lllyasviel/control_v11p_sd15_normalbae"


@dataclass
class IdentityConfig:
    enabled: bool = True
    ip_adapter_model_id: str = "h94/IP-Adapter-FaceID"
    character_id: str | None = None  # coincideix amb metadata.yaml -> identity.character_id
    weight: float = 0.8


@dataclass
class SchedulerConfig:
    type: str = "lcm"
    num_inference_steps: int = 4
    guidance_scale: float = 1.5


@dataclass
class StreamConfig:
    latent_recycling: bool = True
    denoise_strength: float = 0.35  # baix perquè reutilitza latent del frame anterior
    keyframe_interval: int = 1  # 1 = cada frame és keyframe (sense interpolació)


@dataclass
class InterpolationConfig:
    enabled: bool = True
    method: str = "rife"  # "rife" | "blur_fallback"
    target_fps: int = 30
    keyframe_fps: int = 12
    motion_blur_scale: float = 1.0  # multiplica el blur segons magnitud de moviment


@dataclass
class BackendConfig:
    device_preference: list[str] = field(default_factory=lambda: ["cuda", "rocm", "directml", "cpu"])
    dtype: str = "float16"


@dataclass
class PipelineConfig:
    base_model_id: str = "runwayml/stable-diffusion-v1-5"
    resolution: int = 512
    controlnet: ControlNetConfig = field(default_factory=ControlNetConfig)
    identity: IdentityConfig = field(default_factory=IdentityConfig)
    scheduler: SchedulerConfig = field(default_factory=SchedulerConfig)
    stream: StreamConfig = field(default_factory=StreamConfig)
    interpolation: InterpolationConfig = field(default_factory=InterpolationConfig)
    backend: BackendConfig = field(default_factory=BackendConfig)

    @classmethod
    def from_yaml(cls, path: Path | str) -> "PipelineConfig":
        with open(path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
        return cls(
            base_model_id=raw.get("base_model_id", cls.base_model_id),
            resolution=raw.get("resolution", cls.resolution),
            controlnet=ControlNetConfig(**raw.get("controlnet", {})),
            identity=IdentityConfig(**raw.get("identity", {})),
            scheduler=SchedulerConfig(**raw.get("scheduler", {})),
            stream=StreamConfig(**raw.get("stream", {})),
            interpolation=InterpolationConfig(**raw.get("interpolation", {})),
            backend=BackendConfig(**raw.get("backend", {})),
        )

    def to_yaml(self, path: Path | str) -> None:
        from dataclasses import asdict

        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(asdict(self), f, sort_keys=False, allow_unicode=True)
