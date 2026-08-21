from app.retrieval.chunk import chunk_markdown


def test_chunking_tracks_headings_and_keeps_code_blocks_whole() -> None:
    document = """
    # استقرار
    توضیح کوتاه درباره استقرار.

    ```bash
    liara deploy --app sample
    ```

    ## گزارشات
    لاگ برنامه را بررسی کنید.
    """

    chunks = chunk_markdown(document, max_chars=120)

    assert [item.heading for item in chunks] == ["استقرار", "گزارشات"]
    assert "```bash\nliara deploy --app sample\n```" in chunks[0].content
    assert all(len(item.content) <= 120 for item in chunks)
