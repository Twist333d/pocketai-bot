# Define variables for common commands
POETRY = poetry
PYTHON = $(POETRY) run python
SHELL = /bin/bash -e

# Default target executed when no arguments are given to make
all: install

# Install dependencies using Poetry
install:
	$(POETRY) install

# Run tests
test:
	$(POETRY) run pytest

# Clean up the environment (customized to ensure compatibility)
clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -exec rm -rf {} +

# Copy local hooks to the directory and ensure they are executable
setup-hooks:
	cp git_hooks/* .git/hooks/
	chmod +x .git/hooks/*

# Define phony targets for non-file targets
.PHONY: all install test clean setup-hooks