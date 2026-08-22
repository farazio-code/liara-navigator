import pytest
from app.retrieval.anchors import validate_rendered_anchor


def test_heading_anchor_must_exist_in_rendered_page() -> None:
    validate_rendered_anchor(
        "https://docs.liara.ir/paas/details/logs#view-logs",
        rendered_anchors={"overview", "view-logs"},
    )

    with pytest.raises(ValueError, match="broken source anchor"):
        validate_rendered_anchor(
            "https://docs.liara.ir/paas/details/logs#missing",
            rendered_anchors={"overview", "view-logs"},
        )
