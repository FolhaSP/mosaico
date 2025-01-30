.DEFAULT_GOAL := all

# Checa se o uv está instalado
.PHONY: .uv
.uv:
	@uv --version || echo 'Please install uv: https://docs.astral.sh/uv/getting-started/installation/'

# Checa se o pre-commit está instalado
.PHONY: .pre-commit
.pre-commit:
	@pre-commit -V || echo 'Please install pre-commit: https://pre-commit.com/'

# Instala dependências do projeto
.PHONY: install
install: .uv .pre-commit
	uv sync --frozen --all-extras
	uv run pre-commit install --install-hooks

# Padroniza código do projeto
.PHONY: lint
lint:
	uv run ruff check . --fix

# Formata código do projeto
.PHONY: format
format:
	uv run ruff format .

# Executa casos de teste
.PHONY: test
test:
	uv run pytest

.PHONY: e2e
e2e:
	uv run pytest e2e

# Cria documentação
.PHONY: docs
docs:
	uv run mkdocs build

# Serve documentação
.PHONY: docs-serve
docs-serve:
	uv run mkdocs serve --no-strict

.PHONY: all
all: lint format test
