from app.application.router import route_topic


def test_explicit_topic_is_authoritative_and_paas_requires_runtime_context() -> None:
    assert route_topic("dns").knowledge_topic == "dns"
    assert route_topic("dns").requires_runtime_context is False
    assert route_topic("paas").knowledge_topic == "paas"
    assert route_topic("paas").requires_runtime_context is True
