
# MCQ Generation using LLM

Generating Multi-Choices Questions (MCQ) that evaluates diverse knowledge of the test takers is often 
very challenging and time-consuming task. Large Language Models (LLMs) hold a promising method that can 
be useful while meeting the objectives of the MCQ.

## Using the Power of AI in Question Generation

Our MCQ Generator leverages new AI models, including **OpenAI's GPT** and the **open-source Ollama framework**, to generate thoughtful, relevant, and challenging questions. These models allow the tool to create questions that are not only grammatically accurate but also contextually relevant, tailored to various subjects and difficulty levels.

### Key Features

#### 1. Flexible Model Selection
Choose between OpenAI's GPT models or the open-source Ollama framework to suit your needs, whether you're looking for performance, cost-efficiency, or specific use cases.

#### 2. Customizable Question Generation
Tailor your quiz to perfection with these CLI options:
- **Field**: Subject area for question generation (required).
- **Subfield**: Optional sub-category within the field.
- **Difficulty Level**: Select from easy, medium, or hard (default: medium).
- **Number of Questions**: Choose how many questions to generate (default: 5).
- **Options per Question**: Define the number of answer choices (required, must be > 1).
- **Correct Answers**: Set number of correct answers per question (default: 1).
  - Use `0` for "None of the Above" questions
  - Use value equal to options count for "All of the Above" questions
- **Maximum Token Limit**: Adjust the token limit for LLM response (default: 3000).

#### 3. Comprehensive Question Analysis
For every generated question, users can:
- **Check the Correct Answer**: Instantly verify the solution.
- **Request a Detailed Explanation**: Gain insights into why the answer is correct or incorrect.
- **Access Prerequisite Knowledge**: Understand any foundational concepts needed for the question.
- **Translate the Question**: Convert the question to different languages (currently supporting English and Hindi).

#### 4. Intelligent Caching
Our caching system optimizes performance by minimizing redundant API calls. If a question's explanation, prerequisites, or translation has been generated before, the system retrieves it instantly from memory.

#### 5. Unique Question Identification
Each generated question is assigned a unique identifier, making it easy to track, reference, and reuse specific questions. This identifier includes the specialization and a counter for easy question management.

## CLI Usage

The MCQ Generator provides a command-line interface for question generation:

```bash
python mcq_generate_cli.py \
  --field "Physics" \
  --subfield "Mechanics" \
  --difficulty hard \
  --count 5 \
  --options 4 \
  --correct-answers 1 \
  --provider perplexity \
  --model sonar \
  --save questions.json
```

### Arguments:
- `--field`, `-f` (required): Subject field for questions
- `--subfield`, `-sf` (optional): Sub-category within the field
- `--difficulty`, `-d` (default: medium): Easy, medium, or hard
- `--count`, `-c` (default: 5): Number of questions to generate
- `--options`, `-o` (required): Number of options per question (> 1)
- `--correct-answers` (default: 1): Number of correct answers per question
  - `0`: Generates "None of the Above" questions
  - Equal to `--options`: Generates "All of the Above" questions
- `--max-tokens` (default: 3000): Maximum tokens for LLM response
- `--provider` (default: perplexity): LLM provider (openai, claude, perplexity, litellm)
- `--model` (default: sonar): Model name specific to the provider
- `--save`: Output JSON file (auto-generated filename if not specified)

## Technical Detail

The **MCQ Generator** is built using Python with the **LiteLLM** library, providing a unified interface for multiple LLM providers. The system includes:

- **mcq_generate_cli.py**: Command-line interface with argument parsing and validation
- **MCQGenerationEngine**: Core engine managing question generation and display
- **QuestionGenerator**: Handles LLM API calls via LiteLLM and response parsing
- **PromptBuilder**: Creates optimized prompts with 20+ competitive exam rules

The system ensures content meets factual accuracy and adheres to educational best practices through comprehensive prompt engineering.

## Real-World Applications

This tool has a broad range of applications across various fields:
- **Education**: Teachers can quickly generate quizzes for assessments or homework.
- **E-Learning Platforms**: Content creators can generate quizzes that complement their online courses.
- **Corporate Training**: HR departments can create skill evaluation tests for employees.
- **Test Prep Companies**: Generate practice questions for standardized tests like SAT, GRE, etc.
- **Gamified Learning Apps**: Integrate endless MCQs into educational games for dynamic learning experiences.

## Testing

The MCQ Generator includes comprehensive unit tests covering all major components:

```bash
python -m unittest test_mcq_generator -v
```

### Test Coverage:
- **PromptBuilder**: 11 tests covering all prompt generation methods
- **QuestionGenerator**: 11 tests covering parsing and answer extraction
- **MCQGenerationEngine**: 6 tests covering validation and display
- **Total**: 28 tests, 100% pass rate

### Key Test Scenarios:
- Dynamic option generation (2-6 options)
- Multiple answer formats (comma-separated, "and", special cases)
- "All of the Above" and "None of the Above" handling
- Input validation and error handling
- Edge cases and boundary conditions

## Looking Ahead

The future of the MCQ Generator is bright, with planned enhancements such as:
- **Support for More Languages**: Expand multilingual question generation.
- **LMS Integration**: Seamlessly connect to popular learning management systems.
- **Advanced Analytics**: Track question performance and difficulty for continuous improvement.
- **Collaborative Features**: Enable team-based question creation and curation.
- **Batch Processing**: Generate multiple question sets in a single operation.

## Conclusion

The **AI-powered MCQ Generator** may be useful to educators, content creators, and e-learning professionals. By automating the creation of high-quality, tailored multiple-choice questions, this tool not only saves time but also opens up new avenues for personalized learning, adaptive testing, and data-driven insights.

We invite educators, trainers, and quiz enthusiasts to experience how AI is revolutionizing quiz creation. With the MCQ Generator, high-quality educational content becomes more **accessible**, **adaptable**, and **engaging** than ever before.

