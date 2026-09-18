from app.pipeline.cleaning.cleaner import clean_record, clean_text


def test_clean_text_removes_html_and_whitespace() -> None:
    assert clean_text("  <b>Example</b>\n scholarship  ") == "Example scholarship"


def test_clean_record_removes_empty_values() -> None:
    assert clean_record({"name": " Example ", "provider": "", "amount": None}) == {
        "name": "Example"
    }