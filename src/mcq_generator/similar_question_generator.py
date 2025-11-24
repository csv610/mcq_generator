import litellm
from prompt_builder import PromptBuilder

class SimilarQuestionGenerator:
    def __init__(self, model):
        self.model = model
        self.prompt_builder = PromptBuilder()

    def generate_similar_question(self, question, options=None):
        with_options = options is not None
        prompt = self.prompt_builder.get_similar_question_generation_prompt(question, with_options=with_options)
        try:
            response = litellm.completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception:
            return ""

if __name__ == "__main__":
    # Example usage with options
    model = "openai/gpt-4o-mini"
    generator = SimilarQuestionGenerator(model)
    question = "What are the benefits of exercise?"
    options = ["A) Weight loss", "B) Improved mood", "C) Increased energy", "D) All of the above"]
    similar_question = generator.generate_similar_question(question, options)
    print(similar_question)
