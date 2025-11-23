import litellm
from prompt_builder import PromptBuilder

class QuestionTranslator:
    def __init__(self, model):
        self.model = model
        self.prompt_builder = PromptBuilder()

    def translate_text(self, text, language):
        prompt = self.prompt_builder.get_text_translation_prompt(text, language)
        try:
            response = litellm.completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            return text
