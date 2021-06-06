.PHONY: check, format, req, test, run

check:
	@poetry run black peoples_advisor --check
	@poetry run pylama
	@poetry run mypy peoples_advisor

format:
	@poetry run black peoples_advisor

req:
	@poetry export -o peoples_advisor/requirements.txt --without-hashes

test:
	@poetry run pytest

run:
	@poetry run python peoples_advisor/setup.py
	@poetry run python peoples_advisor/main.py
