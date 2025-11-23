# MCQ Generator CLI - Complete Documentation Index

Welcome to the MCQ Generator Command-Line Interface! This folder contains everything you need to generate high-quality multiple-choice questions using AI.

## 📚 Documentation Files

### Getting Started
- **[SETUP.md](SETUP.md)** - Complete setup and installation guide
  - Prerequisites
  - Installation steps
  - API key configuration
  - Troubleshooting
  - First run tutorial

### Quick Reference
- **[QUICK_START.md](QUICK_START.md)** - Fast reference guide
  - 5-minute setup
  - Common commands
  - Popular patterns
  - Quick examples

### Detailed Usage
- **[CLI_USAGE.md](CLI_USAGE.md)** - Complete command documentation
  - All commands explained
  - Options and parameters
  - Full workflow examples
  - JSON file format
  - Logging information

### Features Overview
- **[CLI_FEATURES.md](CLI_FEATURES.md)** - Feature highlights
  - All capabilities
  - AI provider support
  - Use cases
  - Performance notes
  - Architecture overview

### Main Application
- **[cli.py](cli.py)** - The CLI application itself
  - Built with Python's argparse
  - ~500 lines of code
  - Modular and extensible

## 🚀 Quick Start (30 seconds)

```bash
# 1. Install dependencies (if not done)
source venv/bin/activate
pip install openai litellm python-dotenv requests

# 2. Set up API key
echo "OPENAI_API_KEY=sk-..." > .env

# 3. Initialize model
python cli.py init-model --provider openai

# 4. Generate questions
python cli.py generate -s "Python" -c 5 --save questions.json

# 5. View them
python cli.py load questions.json --show-answers
```

## 📖 Command Overview

```bash
# Initialize AI model
python cli.py init-model --provider openai --model gpt-4o-mini

# Generate questions
python cli.py generate --specialization "Python" --count 5

# Load saved questions
python cli.py load questions.json --show-answers

# Get explanation for a question
python cli.py explain questions.json --question-num 1

# Translate to another language
python cli.py translate questions.json -l hindi --save

# Get prerequisite knowledge
python cli.py prerequisites questions.json --question-num 2

# Generate similar question
python cli.py similar questions.json --question-num 1

# Show information
python cli.py info
```

## 🎯 Common Workflows

### For Teachers
1. Generate topic-specific quizzes
2. Save to JSON for organization
3. Export answers for grading
4. Generate similar questions for practice

### For Students
1. Generate practice questions
2. Get explanations for difficult concepts
3. Learn prerequisites before attempting
4. Practice variations with similar questions

### For Content Creators
1. Bulk generate question banks
2. Translate for multilingual audiences
3. Organize by specialization
4. Export in standardized format

## 📋 Features

✅ **AI-Powered Generation** - Generate questions using OpenAI, Claude, or any LiteLLM provider
✅ **Customizable Difficulty** - Easy, Medium, Hard levels
✅ **Bulk Operations** - Generate 1-100+ questions at once
✅ **Multi-Language Support** - Translate to Hindi, Spanish, French
✅ **Detailed Explanations** - Get AI-generated explanations
✅ **Prerequisite Knowledge** - Learn background material
✅ **Question Variations** - Generate similar questions for practice
✅ **Clean JSON Format** - Standard format for integration
✅ **Comprehensive Logging** - Track all operations
✅ **Professional CLI** - Built with argparse

## 🔧 Requirements

- Python 3.7+
- openai package
- litellm package
- python-dotenv package
- requests package

## 📖 Reading Order

1. **First time?** → Start with [SETUP.md](SETUP.md)
2. **In a hurry?** → Check [QUICK_START.md](QUICK_START.md)
3. **Need details?** → Read [CLI_USAGE.md](CLI_USAGE.md)
4. **Want features list?** → See [CLI_FEATURES.md](CLI_FEATURES.md)

## 💡 Tips

- Start with 3-5 questions to test
- Use `gpt-4o-mini` for fast, affordable generation
- Add `--show-answers` to see correct answers immediately
- Use `--save` to persist questions
- Check `mcq_cli.log` for debugging

## 🛠️ Troubleshooting

Most issues are covered in [SETUP.md](SETUP.md) troubleshooting section.

**Common issues:**
- "ModuleNotFoundError" → Install dependencies
- "Failed to initialize model" → Check API key in .env
- "File not found" → Generate questions first
- "Invalid question number" → Use number within range

## 📚 Example Commands

```bash
# Simple generation
python cli.py generate -s "Biology" -c 5

# With save
python cli.py generate -s "Python" -c 3 --save python.json

# Show answers while viewing
python cli.py load python.json --show-answers

# Hard difficulty questions
python cli.py generate -s "Math" -d hard -c 5

# Generate and get explanation
python cli.py generate -s "Physics" -c 1 --save physics.json
python cli.py explain physics.json -q 1

# Multi-language workflow
python cli.py generate -s "Chemistry" -c 5 --save chemistry.json
python cli.py translate chemistry.json -l hindi --save

# Get learning materials
python cli.py prerequisites chemistry.json -q 1

# Practice variations
python cli.py similar chemistry.json -q 1
```

## 🔐 Security Notes

- Never commit your `.env` file (it's in .gitignore)
- Keep API keys private and secure
- Don't share `.env` files with others
- Use environment variables for CI/CD

## 📊 Generated File Format

Questions are saved in this JSON format:
```json
{
  "specialization": "Python",
  "generated_at": "2024-11-23T10:30:45.123456",
  "question_count": 5,
  "questions": [
    {
      "question": "What is...",
      "options": {
        "A": "Option A",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D"
      },
      "correct_answer": "B"
    }
  ]
}
```

## 🚀 Getting Help

```bash
# See all commands
python cli.py --help

# Get help for specific command
python cli.py generate --help
python cli.py explain --help
python cli.py translate --help

# View CLI info
python cli.py info
```

## 📝 Notes

- Questions are AI-generated; always review for accuracy
- Generation time depends on model and question complexity
- Translation quality varies by language and model
- Keep backup of important question files

## 🎓 Educational Use

This tool is perfect for:
- Creating practice question banks
- Generating homework/quizzes
- Building test preparation materials
- Creating multilingual educational content
- Supporting self-paced learning

## 📞 Support

For issues:
1. Check relevant documentation file
2. Review troubleshooting section
3. Check `mcq_cli.log` for error details
4. Verify API key and credentials

## 🎉 Next Steps

1. Complete setup from [SETUP.md](SETUP.md)
2. Try the quick start examples
3. Generate your first question set
4. Explore advanced features

---

**Happy question generating!** 🚀

For detailed information, see the individual documentation files listed above.
