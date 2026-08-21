from app.retrieval.source_policy import is_allowed_source


def test_only_official_document_pages_are_allowed() -> None:
    assert is_allowed_source("https://docs.liara.ir/paas/django/how-tos/deploy-app")
    assert is_allowed_source(
        "https://github.com/liara-cloud/docs/blob/master/src/pages/paas/django/index.mdx"
    )
    assert not is_allowed_source("https://github.com/liara-cloud/docs/issues/42")
    assert not is_allowed_source("https://github.com/liara-cloud/docs/pull/17")
    assert not is_allowed_source("https://example.com/liara-guide")
