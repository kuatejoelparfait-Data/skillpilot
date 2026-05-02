import anthropic

MODEL = "claude-haiku-4-5-20251001"

class ClaudeClient:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Clé API manquante. Lance: devpilot init")
        self._client = anthropic.Anthropic(api_key=api_key)

    def run(self, skill_prompt: str, user_input: str) -> str:
        message = self._client.messages.create(
            model=MODEL,
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": f"{skill_prompt}\n\n---\n\n{user_input}"
            }]
        )
        return message.content[0].text
