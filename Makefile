.PHONY: help venv install act test run clean cleandirs lint format

help:
	@echo "MCQ Generator - Available commands:"
	@echo "  make venv         - Create virtual environment"
	@echo "  make act          - Activate virtual environment"
	@echo "  make install      - Install dependencies"
	@echo "  make test         - Run unit tests"
	@echo "  make run          - Run CLI (requires arguments)"
	@echo "  make clean        - Remove generated files and cache"
	@echo "  make cleandirs    - Remove virtual environment and build files"
	@echo "  make lint         - Run code linting"
	@echo "  make format       - Format code with black"

venv:
	python3 -m venv mcqenv
	. mcqenv/bin/activate && pip install --upgrade pip

act:
	@echo "To activate the virtual environment, run:"
	@echo "  source mcqenv/bin/activate"

shell:
	bash -c 'source mcqenv/bin/activate && bash'

install: venv
	. mcqenv/bin/activate && pip install -r requirements.txt

test:
	. mcqenv/bin/activate && python -m unittest discover tests -v

run:
	. mcqenv/bin/activate && python mcq_generate_cli.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".DS_Store" -delete
	rm -rf .pytest_cache .coverage htmlcov
	rm -f mcq_generate.log mcq_*.json

cleandirs: clean
	rm -rf mcqenv
	rm -rf build dist *.egg-info
	find . -type d -name .eggs -exec rm -rf {} + 2>/dev/null || true

lint:
	. mcqenv/bin/activate && python -m flake8 --max-line-length=100 mcq_generator.py mcq_generate_cli.py question_generator.py

format:
	. mcqenv/bin/activate && python -m black --line-length=100 mcq_generator.py mcq_generate_cli.py question_generator.py
