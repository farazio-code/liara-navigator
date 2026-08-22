from dataclasses import dataclass
from typing import Literal

Topic = Literal["paas", "cdn", "ssl", "dns", "other"]


@dataclass(frozen=True, slots=True)
class RouteDecision:
    knowledge_topic: Topic
    requires_runtime_context: bool


def route_topic(topic: Topic) -> RouteDecision:
    return RouteDecision(knowledge_topic=topic, requires_runtime_context=topic == "paas")
