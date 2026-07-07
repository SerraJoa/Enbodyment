import pytest

from embodiment_visual.backend import detect_available_backends, select_backend, warn_if_underpowered


def test_cpu_always_available():
    backends = detect_available_backends()
    names = [b.name for b in backends]
    assert "cpu" in names


def test_select_backend_respects_preference_order():
    backend = select_backend(["cuda", "rocm", "directml", "cpu"])
    # en aquesta màquina (CPU-only, provat manualment) hauria de caure a cpu
    assert backend.name == "cpu"


def test_warn_if_underpowered_warns_on_cpu():
    backend = select_backend(["cpu"])
    with pytest.warns(RuntimeWarning):
        warn_if_underpowered(backend)
