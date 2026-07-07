from pathlib import Path

from embodiment_visual.config import PipelineConfig


def test_default_config_roundtrip(tmp_path: Path):
    cfg = PipelineConfig()
    out = tmp_path / "config.yaml"
    cfg.to_yaml(out)

    loaded = PipelineConfig.from_yaml(out)

    assert loaded.base_model_id == cfg.base_model_id
    assert loaded.resolution == cfg.resolution
    assert loaded.controlnet.model_id == cfg.controlnet.model_id
    assert loaded.stream.denoise_strength == cfg.stream.denoise_strength


def test_partial_yaml_overrides_only_given_fields(tmp_path: Path):
    out = tmp_path / "partial.yaml"
    out.write_text("resolution: 768\ncontrolnet:\n  conditioning_scale: 0.5\n", encoding="utf-8")

    cfg = PipelineConfig.from_yaml(out)

    assert cfg.resolution == 768
    assert cfg.controlnet.conditioning_scale == 0.5
    assert cfg.controlnet.model_id == "lllyasviel/control_v11f1p_sd15_depth"  # default intacte
