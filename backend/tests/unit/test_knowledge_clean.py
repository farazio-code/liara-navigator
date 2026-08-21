from app.retrieval.clean import clean_document


def test_clean_document_removes_executable_and_navigation_content() -> None:
    raw = """
    import Layout from '@/components/Layout'
    # استقرار Django
    <nav>منوی سایت</nav>
    متن معتبر مستندات.
    <script>steal()</script>
    ```bash
    liara deploy
    ```
    """

    cleaned = clean_document(raw)

    assert "import Layout" not in cleaned
    assert "منوی سایت" not in cleaned
    assert "steal" not in cleaned
    assert "متن معتبر مستندات" in cleaned
    assert "liara deploy" in cleaned
