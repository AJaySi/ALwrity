from utils.asset_tracker import KNOWN_PRODUCER_MODULES, normalize_source_module


def test_all_known_producer_modules_map_to_asset_source() -> None:
    for module_name in sorted(KNOWN_PRODUCER_MODULES):
        normalized = normalize_source_module(module_name)
        assert normalized.value == module_name


def test_legacy_aliases_map_to_canonical_asset_source() -> None:
    assert normalize_source_module("video_generator").value == "video_studio"
    assert normalize_source_module("video-creator").value == "video_studio"
    assert normalize_source_module("campaign_builder").value == "campaign_creator"
