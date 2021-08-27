.PHONY: all
all: tests


.venv/.flag: .python-version poetry.lock
	@poetry config --local virtualenvs.in-project true
	@cmp --silent .python-version .venv/.flag || rm -rf .venv
	@poetry install --remove-untracked
	@cp .python-version .venv/.flag
	@touch .python-version

.PHONY: deps
deps: .venv/.flag


.PHONY: format
format: isort black

.PHONY: isort
isort: deps
	poetry run isort .
	@echo ''

.PHONY: black
black: deps
	poetry run black .
	@echo ''


.PHONY: test tests
test: tests
tests: isort_check black_check mypy pylint

.PHONY: isort_check
isort_check: deps
	poetry run isort --check .
	@echo ''

.PHONY: black_check
black_check: deps
	poetry run black --check .
	@echo ''

.PHONY: mypy
mypy: deps
	poetry run mypy --namespace-packages --explicit-package-bases .
	@echo ''

.PHONY: pylint
pylint: deps
	find . -name '*.py' -not -path './.*' | xargs poetry run pylint --disable=fixme
	@echo ''


.PHONY: run
run: deps
	poetry run python app.py
