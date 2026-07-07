"""Pipeline de difusió en temps real de la branca visual (veure docs/architecture.md §5).

Aquest paquet és scaffolding: l'estructura i la lògica pura (config, warp,
gestió d'estat) estan escrites i provades; les etapes que depenen de models
pesats (ControlNet, IP-Adapter, LCM, RIFE) són interfícies llestes per
connectar-hi els pesos quan hi hagi GPU (Strix Halo) — vegeu cada mòdul.
"""

__all__ = ["config", "backend", "warp", "interpolate", "gbuffer", "pipeline", "stages"]
