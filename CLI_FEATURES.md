# MCQ Generator CLI - Features & Capabilities

## Overview

A powerful command-line interface for generating, managing, and analyzing multiple-choice questions using AI models. Built with Python's `argparse` for a professional CLI experience.

## Core Features

### ✅ Question Generation
- Generate MCQ questions on any topic/specialization
- Adjustable difficulty levels: Easy, Medium, Hard
- Control question count: 1 to 100+ questions
- Customizable token limits for generation
- Fast batch generation

**Command:**
```bash
python cli.py generate --specialization "Python" --count 5
```

### ✅ Multiple AI Provider Support
- **OpenAI**: GPT-4o-mini, GPT-4o, GPT-4
- **Claude**: Claude 3.5 Sonnet, Claude 3.5 Haiku via LiteLLM
- **Other LiteLLM Providers**: Ollama, Cohere, etc.

**Command:**
```bash
python cli.py init-model --provider openai --model gpt-4o-mini
```

### ✅ Question Management
- Save questions to JSON format
- Load previously generated questions
- Store metadata (specialization, generation time, count)
- Organize questions by topic

**Commands:**
```bash
python cli.py load questions.json --show-answers
python cli.py generate -s "Biology" --save biology.json
```

### ✅ Question Analysis
- Display correct answers
- Generate detailed explanations for questions
- Get prerequisite knowledge/background material
- Customizable explanation depth

**Command:**
```bash
python cli.py explain questions.json --question-num 1
```

### ✅ Question Variations
- Generate similar questions based on existing ones
- Useful for creating practice sets
- Maintains topic relevance while varying question text

**Command:**
```bash
python cli.py similar questions.json --question-num 1
```

### ✅ Multi-Language Support
- Translate questions to different languages
- Supported languages: Hindi, Spanish, French
- Save translated versions separately
- Batch translation of all questions

**Command:**
```bash
python cli.py translate questions.json -l hindi --save
```

### ✅ Prerequisite Knowledge
- Get background material for understanding a question
- Helps learners with foundational concepts
- AI-generated learning aids

**Command:**
```bash
python cli.py prerequisites questions.json --question-num 2
```

## Technical Features

### 🔧 Logging & Debugging
- Comprehensive logging to `mcq_cli.log`
- All operations tracked for debugging
- Error details captured for troubleshooting

### 📊 Data Format
Questions stored in clean JSON format:
```json
{
  "specialization": "Python Programming",
  "generated_at": "2024-11-23T10:30:45.123456",
  "question_count": 5,
  "questions": [
    {
      "question": "What is the output of print(2 ** 3)?",
      "options": {
        "A": "6",
        "B": "8",
        "C": "9",
        "D": "5"
      },
      "correct_answer": "B"
    }
  ]
}
```

### 🔌 Modular Architecture
- `MCQGeneratorCLI` class handles core operations
- `QuestionGenerator` generates questions
- `QuestionTranslator` handles translations
- `QuestionPrerequisite` generates background material
- `SimilarQuestionGenerator` creates variations

### 🛡️ Error Handling
- Graceful error messages
- Validation of inputs
- File existence checks
- Model initialization verification
- Question number range validation

## Command Reference

| Command | Purpose | Key Options |
|---------|---------|------------|
| `init-model` | Initialize AI model | `--provider`, `--model` |
| `generate` | Generate MCQ questions | `--specialization`, `--difficulty`, `--count`, `--save` |
| `load` | Load and display questions | `--show-answers` |
| `explain` | Get explanation for a question | `--question-num`, `--max-tokens` |
| `translate` | Translate questions | `--language`, `--save` |
| `prerequisites` | Get background knowledge | `--question-num` |
| `similar` | Generate similar question | `--question-num` |
| `info` | Show CLI information | - |

## Use Cases

### 1️⃣ Education
- Teachers generating quizzes for students
- Creating practice tests
- Building question banks

### 2️⃣ Exam Preparation
- Generate practice questions for SAT, GRE, etc.
- Create topic-specific test papers
- Translate questions for language learners

### 3️⃣ Self-Learning
- Get explanations for complex topics
- Learn prerequisites before attempting questions
- Practice variations of similar questions

### 4️⃣ Content Creation
- Build question databases for e-learning platforms
- Create multilingual quizzes
- Generate questions in bulk for courses

### 5️⃣ Corporate Training
- Create employee skill assessments
- Generate certification test questions
- Build training materials

## Workflow Examples

### Quick Test Generation
```bash
python cli.py init-model --provider openai
python cli.py generate -s "Biology" -c 5 --save bio.json
python cli.py load bio.json --show-answers
```

### Comprehensive Learning Path
```bash
# Generate questions
python cli.py generate -s "Python" -c 3 --save python.json

# Study them
python cli.py load python.json

# Understand concepts
python cli.py prerequisites python.json -q 1

# Get explanations
python cli.py explain python.json -q 1

# Practice variations
python cli.py similar python.json -q 1

# Translate for practice
python cli.py translate python.json -l spanish --save
```

### Bulk Question Bank Creation
```bash
# Generate for multiple topics
python cli.py generate -s "Physics" -c 10 --save physics.json
python cli.py generate -s "Chemistry" -c 10 --save chemistry.json

# Translate to multiple languages
python cli.py translate physics.json -l hindi --save
python cli.py translate physics.json -l spanish --save
```

## Performance Characteristics

- **Question Generation**: ~10-20 seconds per question (depends on model)
- **Loading Questions**: <100ms
- **Translation**: ~3-5 seconds per question
- **Explanations**: ~10-15 seconds per question
- **JSON File Size**: ~50-100KB per 10 questions

## Limitations & Notes

- Requires valid API keys for chosen provider
- Model selection affects quality and cost
- Longer max-tokens mean longer generation time
- Translation quality depends on source language
- Some models may have rate limiting

## Future Enhancements

Potential additions:
- CSV export format
- Image-based question generation
- Question difficulty analysis
- User performance tracking
- Question difficulty ranking
- Batch operations
- Configuration files for defaults
- Interactive mode

---

For detailed usage, see `CLI_USAGE.md`
For quick start, see `QUICK_START.md`
