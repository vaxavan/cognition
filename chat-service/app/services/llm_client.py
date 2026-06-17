class DeepSeekYandexClient:
    def __init__(self):
        pass

    async def stream_text(self, system_prompt: str, user_prompt: str, temperature: float = 0.7, max_tokens: int = 2048):
        """Заглушка — возвращает тестовый ответ"""
        test_response = f"Привет! Это тестовый ответ от Cognition. Ты спросил: '{user_prompt}'. Я пока работаю без нейросети."
        for word in test_response.split():
            yield word + " "