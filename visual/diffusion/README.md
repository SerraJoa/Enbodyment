# diffusion — branca visual (pipeline de difusió)

Implementa architecture.md §5: ControlNet (depth/normal) + IP-Adapter FaceID +
LCM + StreamDiffusion (latent recycling) + warp per motion vectors +
interpolació piramidal.

## Estat: provat vs pendent

Aquesta màquina de desenvolupament és CPU-only (Ryzen 8500G, sense CUDA/ROCm
útil) — **no es pot córrer el pipeline de difusió real aquí**. El que sí
s'ha escrit i provat (`pytest`, veure `tests/`):

- `config.py` — càrrega/desa YAML de configuració.
- `warp.py` — warp per motion vectors, màscara de desoclusió, magnitud.
- `gbuffer.py` — càrrega dels render passes exportats pel motor.
- `stages/stream.py` (`LatentRecycler`) — barreja de latents amb tensors dummy.
- `interpolate.py` (`FrameInterpolator`) — fallback blend+blur (RIFE real pendent).
- `backend.py` — detecció de backend (confirma que aquesta màquina cau a CPU).

**Pendent, requereix GPU real (Strix Halo) per provar-ho de veritat:**
- `stages/controlnet_stage.py` — càrrega de pesos ControlNet.
- `stages/identity_stage.py` — IP-Adapter FaceID (`.load()` llança `NotImplementedError`
  expressament: falta decidir on es guarden els embeddings per `character_id`).
- `stages/scheduler.py` — substitució per LCMScheduler.
- `pipeline.py` (`VisualPipeline.load/run_keyframe/run_recycled`) — orquestra
  tot l'anterior; `.load()` llança `NotImplementedError` a propòsit fins que
  hi hagi un pipeline de `diffusers` real per connectar.
- Interpolació RIFE real (`interpolate.py` avisa amb `RuntimeWarning` i cau al
  fallback si es demana `method="rife"`).

## Instal·lació

```bash
pip install -e ".[dev]"          # nucli + pytest (el que es pot provar aquí)
pip install -e ".[diffusion]"    # + diffusers/transformers/accelerate (node amb GPU)
pip install -e ".[identity]"     # + IP-Adapter/insightface (node amb GPU)
```

ROCm/DirectML/CUDA per `torch` s'instal·len a banda segons la plataforma real
del node d'inferència — no hi ha una única wheel universal.

## Tests

```bash
pytest
```
