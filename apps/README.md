# Streamlit Applications

This directory contains Streamlit-based web applications for the MCQ Generator.

## Structure

```
apps/
├── streamlit_apps/          # Streamlit applications
│   ├── main.py             # Main MCQ generator web app
│   └── mcq_generator.py    # Alternative Streamlit MCQ generator
└── README.md               # This file
```

## Running the Apps

### Main App
```bash
streamlit run apps/streamlit_apps/main.py
```

### Alternative MCQ Generator
```bash
streamlit run apps/streamlit_apps/mcq_generator.py
```

## Features

### main.py
- Multi-provider LLM support (OpenAI, Claude, Perplexity)
- Question generation with customizable parameters
- Question translation
- Prerequisite analysis
- Similar question generation
- JSON export functionality

### mcq_generator.py
- OpenAI-based MCQ generation
- Question parsing and validation
- Caching for API responses
- Error handling and logging

## Requirements

See `requirements.txt` in the project root for dependencies.

## Notes

- Streamlit apps use the core modules from `src/mcq_generator/`
- Logs are saved in the working directory
- Generated questions can be exported to JSON format
