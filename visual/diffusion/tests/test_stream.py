import torch

from embodiment_visual.config import StreamConfig
from embodiment_visual.stages.stream import LatentRecycler


def test_no_previous_returns_fresh_noise():
    recycler = LatentRecycler(config=StreamConfig(latent_recycling=True))
    noise = torch.randn(1, 4, 8, 8)

    result = recycler.init_latents(noise)

    assert torch.equal(result, noise)


def test_recycles_previous_latents_with_strength():
    recycler = LatentRecycler(config=StreamConfig(latent_recycling=True, denoise_strength=0.0))
    previous = torch.ones(1, 4, 8, 8)
    recycler.update(previous)

    noise = torch.randn(1, 4, 8, 8)
    result = recycler.init_latents(noise)

    # strength=0 -> hauria de tornar el latent anterior tal qual (alpha=1, beta=0)
    assert torch.allclose(result, previous)


def test_disabled_recycling_ignores_previous():
    recycler = LatentRecycler(config=StreamConfig(latent_recycling=False))
    recycler.update(torch.ones(1, 4, 8, 8))

    noise = torch.randn(1, 4, 8, 8)
    result = recycler.init_latents(noise)

    assert torch.equal(result, noise)


def test_invalid_strength_raises():
    recycler = LatentRecycler(config=StreamConfig(latent_recycling=True, denoise_strength=1.5))
    recycler.update(torch.ones(1, 4, 8, 8))

    try:
        recycler.init_latents(torch.randn(1, 4, 8, 8))
        assert False, "hauria d'haver llançat ValueError"
    except ValueError:
        pass
