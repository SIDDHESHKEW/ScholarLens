from app.pipeline.deduplication.deduplicator import fingerprint, is_duplicate


def test_detects_exact_duplicate() -> None:
    first = {"name": "Grant", "provider": "Provider", "official_source_url": "https://x.test"}
    second = {"name": " Grant ", "provider": "Provider", "official_source_url": "https://x.test"}
    assert fingerprint(first) == fingerprint(second)
    assert is_duplicate(first, second)


def test_does_not_merge_different_provider() -> None:
    first = {"name": "Grant", "provider": "Provider A"}
    second = {"name": "Grant", "provider": "Provider B"}
    assert not is_duplicate(first, second)