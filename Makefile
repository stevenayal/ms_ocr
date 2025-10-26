.PHONY: help setup install test fmt lint run clean docker-build docker-run docker-dev

# Variables
PYTHON := python
PIP := pip
DOCKER_IMAGE := ms-ocr
DOCKER_TAG := latest
PDF ?= examples/sample.pdf
OUT ?= examples/output

help:
	@echo "ms-ocr Makefile Commands"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup       - Create virtual environment and install dependencies"
	@echo "  make install     - Install package in development mode"
	@echo ""
	@echo "Development:"
	@echo "  make test        - Run unit tests with coverage"
	@echo "  make fmt         - Format code with black and isort"
	@echo "  make lint        - Lint code with ruff"
	@echo "  make clean       - Clean build artifacts and cache files"
	@echo ""
	@echo "Running:"
	@echo "  make run         - Run ms-ocr on sample PDF (PDF=path/to/file.pdf OUT=output/dir)"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-run    - Run Docker container (PDF=path/to/file.pdf)"
	@echo "  make docker-dev    - Start development container"
	@echo ""

setup:
	$(PYTHON) -m venv venv
	./venv/Scripts/python -m pip install --upgrade pip
	./venv/Scripts/pip install -r requirements.txt
	./venv/Scripts/pip install -e ".[dev]"
	@echo "Setup complete! Activate with: venv\\Scripts\\activate"

install:
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install -e ".[dev]"

test:
	$(PYTHON) -m pytest tests/ -v --cov=src/ms_ocr --cov-report=term-missing --cov-report=html

fmt:
	$(PYTHON) -m black src/ tests/
	$(PYTHON) -m isort src/ tests/

lint:
	$(PYTHON) -m ruff check src/ tests/
	$(PYTHON) -m mypy src/

run:
	$(PYTHON) -m ms_ocr.cli extract --input $(PDF) --out $(OUT) --lang spa,eng --gamma --brand assets/brand.json --logo assets/logo.png

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache .coverage htmlcov/ .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docker-build:
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .

docker-run:
	docker run --rm \
		-v $(PWD)/examples:/data/input \
		-v $(PWD)/examples/output:/data/output \
		-v $(PWD)/assets:/app/assets \
		$(DOCKER_IMAGE):$(DOCKER_TAG) \
		extract --input /data/input/$(notdir $(PDF)) --out /data/output --lang spa,eng --gamma --brand /app/assets/brand.json --logo /app/assets/logo.png

docker-dev:
	docker build --target dev -t $(DOCKER_IMAGE):dev .
	docker run --rm -it \
		-v $(PWD):/app \
		-v $(PWD)/examples:/data/input \
		-v $(PWD)/examples/output:/data/output \
		$(DOCKER_IMAGE):dev
