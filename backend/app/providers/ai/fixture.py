from app.providers.ai.base import CompletionResult


class FixtureAIProvider:
    async def complete(
        self, *, message: str, topic: str, context: list[str]
    ) -> CompletionResult:
        if not context:
            return CompletionResult(claims=[])
        chunk_id, content = context[0].split("\n", 1)
        sentence = content.split(".", 1)[0].strip()
        return CompletionResult(
            claims=[
                {
                    "text": sentence,
                    "role": "core",
                    "chunk_id": chunk_id,
                    "evidence": sentence,
                }
            ]
        )
