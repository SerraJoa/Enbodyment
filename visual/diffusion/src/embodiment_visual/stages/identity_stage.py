"""Identitat via IP-Adapter FaceID (no LoRA per cara — no escala en runtime,
veure architecture.md §5). `character_id` ve de metadata.yaml (identity.character_id),
ortogonal a l'estructura (conventions.md) — mai es barreja amb noms de links/joints.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..config import IdentityConfig


@dataclass
class IdentityAdapter:
    config: IdentityConfig
    _face_embedding = None
    _loaded: bool = False

    def load(self) -> None:
        """Carrega IP-Adapter FaceID. Pesat (i depèn d'insightface per l'embedding
        facial) — no cridar en aquesta màquina."""
        if not self.config.enabled:
            return
        from ip_adapter import IPAdapterFaceID  # noqa: PLC0415  (paquet extern, no instal·lat aquí)

        raise NotImplementedError(
            "Carrega real d'IPAdapterFaceID pendent de connectar amb el checkpoint del "
            "character_id concret — cal decidir on es guarden els embeddings per character_id "
            "(un cop n'hi hagi més d'un) abans d'implementar-ho de veritat."
        )

    def reference_image_path(self, character_id: str, faces_dir: Path) -> Path:
        """Convenció de fitxers: una imatge de referència per character_id,
        `faces_dir/{character_id}.png`. Pura organització, no depèn de cap model."""
        return faces_dir / f"{character_id}.png"
